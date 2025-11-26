import os
import smtplib
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Конфигурация продуктов
PRODUCTS = {
    'stend': {
        'name': 'Стенд для пакеров',
        'links': [
            'https://disk.yandex.ru/d/ваша_ссылка_стенд_1',
            'https://disk.yandex.ru/d/ваша_ссылка_стенд_2',
            'https://disk.yandex.ru/d/ваша_ссылка_стенд_3'
        ]
    },
    'stapel': {
        'name': 'Стапель сварочный 3х12 м', 
        'links': [
            'https://disk.yandex.ru/d/ваша_ссылка_стапель_1',
            'https://disk.yandex.ru/d/ваша_ссылка_стапель_2'
        ]
    },
    'level': {
        'name': 'Уровнемер механический',
        'links': [
            'https://disk.yandex.ru/d/ваша_ссылка_уровнемер_1'
        ]
    }
}

def get_payment_data():
    """Получаем данные о платеже"""
    event_path = os.getenv('GITHUB_EVENT_PATH')
    if event_path and os.path.exists(event_path):
        with open(event_path, 'r') as f:
            event_data = json.load(f)
            return event_data.get('client_payload', {})
    return {}

def send_email(customer_email, customer_name, product_data):
    """Отправляем email с ссылками"""
    try:
        # Настройки почты
        smtp_server = "smtp.mail.ru"
        smtp_port = 587
        sender_email = "irashitov79@mail.ru"
        sender_password = os.getenv('EMAIL_PASSWORD')
        
        # Создаем сообщение
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'FIXCAD MARKET - Ваши файлы: {product_data["name"]}'
        msg['From'] = sender_email
        msg['To'] = customer_email
        
        # Текст письма
        links_text = '\n'.join([f'• {link}' for link in product_data['links']])
        
        text = f"""
Спасибо за покупку в FIXCAD MARKET!

Ваш заказ: {product_data['name']}

Ссылки для скачивания:
{links_text}

Файлы будут доступны в течение 30 дней.

При возникновении проблем пишите на irashitov79@mail.ru

С уважением,
Команда FIXCAD MARKET
"""
        
        # HTML версия письма
        links_html = ''.join([f'<li><a href="{link}">{link}</a></li>' for link in product_data['links']])
        
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
        
        # Прикрепляем обе версии
        msg.attach(MIMEText(text, 'plain'))
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
    print("🚀 Запуск обработки платежа...")
    
    payment_data = get_payment_data()
    if not payment_data:
        print("❌ Нет данных о платеже")
        return
    
    product_id = payment_data.get('product_id')
    customer_email = payment_data.get('customer_email')
    customer_name = payment_data.get('customer_name', '')
    
    if not all([product_id, customer_email]):
        print("❌ Отсутствуют обязательные данные")
        return
    
    product_data = PRODUCTS.get(product_id)
    if not product_data:
        print(f"❌ Продукт {product_id} не найден")
        return
    
    print(f"📦 Обрабатываем: {product_data['name']}")
    print(f"📧 Для: {customer_email}")
    
    # Замените ссылки на реальные с Яндекс.Диска
    print("⚠️ ЗАМЕНИТЕ ССЫЛКИ В КОНФИГУРАЦИИ НА РЕАЛЬНЫЕ!")
    
    # Отправляем email
    success = send_email(customer_email, customer_name, product_data)
    
    if success:
        print("✅ Обработка завершена успешно!")
    else:
        print("❌ Ошибка при отправке email")

if __name__ == '__main__':
    main()
