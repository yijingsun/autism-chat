"""
主应用入口
基于 Gradio 构建自闭症友好对话界面

运行方式：
    python app.py
"""
import gradio as gr
from chain import build_conversation_chain, chat
from rag import load_faiss_index
from prompts import TOPIC_SCENARIOS
from emotion import detect_emotion, get_matched_keywords


# ============================================================
# 全局状态
# ============================================================
faiss_index = None
conversation_chain = None


def init_system():
    """初始化系统：加载 FAISS 索引 + 构建对话链"""
    global faiss_index, conversation_chain
    print("[启动] 正在初始化系统...")
    faiss_index = load_faiss_index()
    conversation_chain = build_conversation_chain(faiss_index)
    print("[启动] 系统初始化完成")


def respond(message: str, history: list) -> str:
    """
    处理用户消息并返回回复

    Args:
        message: 用户输入的文本
        history: Gradio 管理的对话历史（ChatInterface 自动传入）

    Returns:
        模型回复文本
    """
    if not message.strip():
        return "你好呀！我是星星，我们来聊天吧！"

    response = chat(message, conversation_chain)

    # 调试信息（生产环境可关闭）
    emotion = detect_emotion(message)
    keywords = get_matched_keywords(message)
    print(f"[情绪检测] 输入: {message[:30]}... | 情绪: {emotion} | 关键词: {keywords}")

    return response


def reset_conversation():
    """重置对话（清空记忆）"""
    global conversation_chain
    conversation_chain = build_conversation_chain(faiss_index)
    return "好的，我们重新开始吧！你好呀，我是星星！"


# ============================================================
# Gradio 界面
# ============================================================
def create_ui() -> gr.Blocks:
    """构建 Gradio 界面"""

    # 话题按钮配置
    topic_buttons = {
        key: f"🎯 {info['name']}"
        for key, info in TOPIC_SCENARIOS.items()
    }

    with gr.Blocks(
        title="星星对话 - 自闭症友好对话助手",
        theme=gr.themes.Soft(),
        css="""
        .chatbot-container { min-height: 400px; }
        .topic-btn { margin: 2px; }
        """,
    ) as demo:
        gr.Markdown(
            """
            # 🌟 星星对话
            ### 面向自闭症儿童的友好对话助手

            > 我是"星星"，一个耐心、友善的对话小伙伴。
            > 我会用简单的话和你聊天，陪你玩游戏，帮你认识情绪。
            """
        )

        with gr.Row():
            with gr.Column(scale=3):
                chatbot = gr.ChatInterface(
                    fn=respond,
                    type="messages",
                    examples=[
                        "你好！",
                        "我今天很开心",
                        "我有点难过",
                        "我们来数数吧",
                        "你喜欢什么颜色？",
                    ],
                    retry_btn="🔄 再说一次",
                    undo_btn="↩️ 撤回",
                    clear_btn="🗑️ 清空对话",
                )

            with gr.Column(scale=1):
                gr.Markdown("### 🎮 话题选择")
                gr.Markdown("点击按钮切换话题：")

                topic_outputs = []
                for key, label in topic_buttons.items():
                    btn = gr.Button(label, size="sm", elem_classes="topic-btn")
                    topic_outputs.append(btn)

                gr.Markdown("---")
                gr.Markdown("### 📊 系统信息")
                status = gr.Textbox(
                    label="状态",
                    value="✅ 系统运行中",
                    interactive=False,
                )
                rag_status = gr.Textbox(
                    label="知识库",
                    value="已加载" if faiss_index else "未构建（可正常运行）",
                    interactive=False,
                )

                gr.Markdown("---")
                gr.Markdown(
                    """
                    ### 📖 关于本项目
                    本项目是一个面向自闭症儿童的对话 AI 原型系统。

                    **核心特点：**
                    - 语言简短、正向鼓励
                    - 情绪感知与自适应回应
                    - 基于特教知识库的 RAG 增强
                    - 模型无关设计（支持 DeepSeek/OpenAI/Qwen）

                    **技术栈：** LangChain + FAISS + Gradio + DeepSeek
                    """
                )

    return demo


# ============================================================
# 启动
# ============================================================
if __name__ == "__main__":
    init_system()
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860)
