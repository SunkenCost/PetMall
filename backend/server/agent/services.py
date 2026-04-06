import json
from django.conf import settings
from openai import OpenAI
from commodity.models import Product
from shopper.models import PetProfile

# Initialize Zhipu AI client
client = OpenAI(
    api_key=settings.ZHIPU_AI_API_KEY,
    base_url=settings.ZHIPU_AI_BASE_URL
)

def search_products(query="", min_price=None, max_price=None):
    """
    Search for products in the database.
    """
    products = Product.objects.filter(is_deleted=False, status=True)
    if query:
        products = products.filter(name__icontains=query)
    if min_price is not None:
        products = products.filter(price__gte=min_price)
    if max_price is not None:
        products = products.filter(price__lte=max_price)
    
    # Limit to 5 products for AI context
    results = []
    for p in products[:5]:
        results.append({
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "description": p.description[:100] if p.description else "",
            "image": p.main_image.url if p.main_image else ""
        })
    return results

def get_user_pet_profiles(user):
    """
    Retrieve pet profiles for a given user.
    """
    if not user or not user.is_authenticated:
        return []
    
    pets = PetProfile.objects.filter(user=user)
    results = []
    for p in pets:
        results.append({
            "name": p.pet_name,
            "type": p.pet_type,
            "breed": p.breed,
            "gender": "公" if p.gender == 1 else "母" if p.gender == 2 else "未知",
            "birthday": str(p.birthday) if p.birthday else "未知"
        })
    return results

# Tool definitions for Function Calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "根据名称、价格区间搜索宠物商城中的商品信息。返回商品的ID、名称、价格、描述和预览图。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "搜索关键词，如 '猫粮', '布偶猫', '项圈'"
                    },
                    "min_price": {
                        "type": "number",
                        "description": "最低价格"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "最高价格"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_user_pet_profiles",
            "description": "获取当前用户已建立的所有宠物档案信息。包括宠物的名字、品种、性别、生日等。",
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }
]

def get_agent_response(messages, user=None):
    """
    Get response from GLM-4-Flash with tool calling support.
    """
    try:
        # Initial call to model
        response = client.chat.completions.create(
            model=settings.ZHIPU_AI_MODEL,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        
        # If model wants to call a tool
        if tool_calls:
            # Handle tool calls
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "search_products":
                    function_response = search_products(
                        query=function_args.get("query", ""),
                        min_price=function_args.get("min_price"),
                        max_price=function_args.get("max_price")
                    )
                elif function_name == "get_user_pet_profiles":
                    function_response = get_user_pet_profiles(user)
                else:
                    function_response = {"error": "Tool not found"}
                    
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response, ensure_ascii=False)
                })
            
            # Second call to get final text
            second_response = client.chat.completions.create(
                model=settings.ZHIPU_AI_MODEL,
                messages=messages
            )
            return second_response.choices[0].message.content, messages
        
        return response_message.content, messages
    except Exception as e:
        print(f"Agent Error: {e}")
        return "不好意思，我的大脑开小差了，请稍后再试。", messages
