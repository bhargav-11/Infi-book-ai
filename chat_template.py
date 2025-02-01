def load_chat_styles():
    return """
    <style>
        .chat-container {
            background-color: rgba(61, 157, 243, 0.2);
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        /* Rest of your CSS */
    </style>
    """

def get_chat_template():
    return """
    <div class="chat-container">
        <div class="chat-index">#{index}</div>
        <div class="chat-content">
            <h2>{title}</h2>
            {content}
            <div class="download-link-container">
                {download_link}
            </div>
            <div class="source-list">
                {sources}
            </div>
            <div class="source-list">
                {source_links}
            </div>
        </div>
    </div>
    """