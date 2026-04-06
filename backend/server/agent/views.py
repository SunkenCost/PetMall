from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .services import get_agent_response

# Basic prompt to guide the AI behavior
SYSTEM_PROMPT = {
    "role": "system",
    "content": """你是一个名为“小宠”的专业宠物店智能导购助手，服务于“PetMall”宠物商城。
你的任务是：
1. 提供关于宠物饲养、健康和品种的专业建议。
2. 只要涉及商品推荐，必须采取以下步骤：
   - 首先调用 get_user_pet_profiles 获取用户宠物的详细信息（品种、年龄等）。
   - 根据宠物特征，调用 search_products 在本商城搜索最匹配的商品。
   - 严禁推荐 search_products 搜索结果之外的任何商品。
3. 如果用户没有建立宠物档案，请礼貌地建议其去[这里](/#/pets)完善信息，以便提供更精准的推荐。
4. 保持亲切、活泼、充满爱心的语气。当没有搜索到匹配商品时，请如实告知并询问更多细节，不要编造商品。
"""
}

@api_view(['POST'])
def agent_chat(request):
    """
    Handle chat interaction with the user.
    Frontend should send message history.
    """
    history = request.data.get('history', [])
    user_msg = request.data.get('message')
    
    if not user_msg:
        return Response({'detail': '请输入消息'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Construct complete messages list including system prompt
    messages = [SYSTEM_PROMPT] + history + [{"role": "user", "content": user_msg}]
    
    # Get AI response, passing user for context
    ai_content, updated_history = get_agent_response(messages, user=request.user)
    
    # Return response and the new conversation turn
    return Response({
        'reply': ai_content,
        'history': updated_history[1:] # Return without system prompt
    })
