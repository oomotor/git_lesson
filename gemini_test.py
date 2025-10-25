import os
import google.generativeai as genai

# Gemini API設定
genai.configure(api_key="AIzaSyDrvIfo2TmbwA3hIR9-FClXeJ93UPfAep0")  # 実際のAPIキーに置き換え

def test_gemini_chat(message):
    """Gemini APIとの対話テスト"""
    try:
        # Gemini-1.5-flashモデルを使用（高速・低コスト）
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # 日本語での自然な会話を促すプロンプト
        system_prompt = """
        あなたは親しみやすく、丁寧な日本語で会話するアシスタントです。
        簡潔で分かりやすい返答を心がけてください。
        """
        
        full_prompt = f"{system_prompt}\n\nユーザー: {message}\nアシスタント: "
        
        response = model.generate_content(full_prompt)
        return response.text
        
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

if __name__ == "__main__":
    print("Gemini API テスト開始")
    print("終了するには 'quit' と入力してください\n")
    
    while True:
        user_input = input("あなた: ")
        if user_input.lower() == 'quit':
            print("テスト終了")
            break
        
        response = test_gemini_chat(user_input)
        print(f"Gemini: {response}\n")