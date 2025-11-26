import os
import json
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Конфигурация продуктов - ЗАМЕНИТЕ НА РЕАЛЬНЫЕ ССЫЛКИ!
PRODUCTS = {
    'stend': {
        'name': 'Стенд для пакеров',
        'links': [
            'https://disk.yandex.ru/d/ВАША_ССЫЛКА_СТЕНД_1',
            'https://disk.yandex.ru/d/ВАША_ССЫЛКА_СТЕНД_2',
        ]
    },
    'stapel': {
        'name': 'Стапель сварочный 3х12 м',
        'links': [
            'https://disk.yandex.ru/d/ВАША_ССЫЛКА_СТАПЕЛЬ',
        ]
    },
    'level': {
        'name': 'Уровнемер механический',
        'links': [
            'https://disk.yandex.ru/d/ВАША_ССЫЛКА_УРОВНЕМЕР',
        ]
    }
}

def extract_order_from_issue():
    """Извлекаем данные заказа из issue"""
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if not event_path or not os.path.exists(event_path):
        print("❌ Файл события не найден")
        return None
        
    with open(event_path, 'r') as f:
        event_data = json.load(f)
        
    issue = event_data.get('issue', {})
    body = issue.get('body', '')
    
    print(f"📄 Текст issue: {body}")
    
    # Извлекаем данные из issue body
    product_match = re.search(r'-\s*\*\*Товар:\*\*\s*(\w+)', body)
    email_match = re.search(r'-\s*\*\*Email:\*\*\s*([^\s\n]+)', body)
    name_match = re.search(r'-\s*\*\*Имя:\*\*\s*([^\n]+)', body)
    
    if not product_match:
        print("❌ Не найден товар в issue")
        return None
    if not email_match:
        print("❌ Не найден email в issue")
        return None
        
    return {
        'product_id': product_match.group(1),
        'customer_email': email_match.group(1),
        'customer_name': name_match.group(1).strip() if name_match else ''
    }

def send_email(customer_email, customer_name, product_data):
    """Отправляем email с ссылками"""
    try:
        # Настройки почты
        smtp_server = "smtp.mail.ru"
        smtp_port = 587
        sender_email = "irashitov79@mail.ru"
        sender_password = os.getenv('EMAIL_PASSWORD')
        
        if not sender_password:
            print("❌ Пароль email не установлен в секретах")
            return False
        
        # Создаем сообщение
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'FIXCAD MARKET - Ваши файлы: {product_data["name"]}'
        msg['From'] = sender_email
        msg['To'] = customer_email
        
        # HTML версия письма
        links_html = ''.join([f'<li><a href="{link}" style="color: #667eea; text-decoration: none;">{link}</a></li>' for link in product_data['links']])
        
        html = f"""
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: #667eea; color: white; padding: 20px; text-align: center; border-radius: 10px; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 10px; margin-top: 10px; }}
        .footer {{ text-align: center; margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Спасибо за покупку!</h1>
            <p>FIXCAD MARKET</p>
        </div>
        <div class="content">
            <p>Здравствуйте{customer_name and ', ' + customer_name or ''}!</p>
            <p>Ваш заказ <strong>«{product_data['name']}»</strong> успешно обработан.</p>
            
            <h3>📥 Ссылки для скачивания:</h3>
            <ul>
                {links_html}
            </ul>
            
            <p><strong>⚠️ Важно:</strong></p>
            <ul>
                <li>Ссылки действительны 30 дней</li>
                <li>Для скачивания нажмите на ссылку</li>
                <li>При проблемах пишите нам</li>
            </ul>
            
            <p>С уважением,<br>
            <strong>Команда FIXCAD MARKET</strong><br>
            📧 irashitov79@mail.ru</p>
        </div>
        <div class="footer">
            <p>Это письмо отправлено автоматически</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Прикрепляем HTML версию
        msg.attach(MIMEText(html, 'html'))
        
        # Отправляем
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email отправлен на {customer_email}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки email: {str(e)}")
        return False

def main():
    print("🚀 Запуск обработки заказа из issue...")
    
    order_data = extract_order_from_issue()
    if not order_data:
        print("❌ Не удалось извлечь данные заказа")
        return
        
    product_id = order_data['product_id']
    customer_email = order_data['customer_email']
    customer_name = order_data['customer_name']
    
    print(f"📦 Товар: {product_id}")
    print(f"📧 Email: {customer_email}")
    print(f"👤 Имя: {customer_name}")
    
    # Проверяем продукт
    product_data = PRODUCTS.get(product_id)
    if not product_data:
        print(f"❌ Продукт {product_id} не найден")
        return
    
    print(f"🎯 Обрабатываем: {product_data['name']}")
    
    # Отправляем email
    success = send_email(customer_email, customer_name, product_data)
    
    if success:
        print("✅ Обработка завершена успешно!")
    else:
        print("❌ Ошибка при отправке email")

if __name__ == '__main__':
    main()
