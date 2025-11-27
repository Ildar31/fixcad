const express = require('express');
const bodyParser = require('body-parser');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(require('cors')());

// ============================================
// ВАШИ ССЫЛКИ С ЯНДЕКС.ДИСКА
// ============================================
const PRODUCTS = {
  stend: {
    name: 'Стенд для пакеров',
    description: 'Полный комплект чертежей и 3D модель',
    zipUrl: 'https://disk.yandex.ru/d/yavUz8k9ce2gAw/download',
    zipName: 'stend.zip',
    contents: [
      'Чертежи КОМПАС (CDW)',
      '3D модели КОМПАС (A3D, M3D)',
      'Спецификации (SPW)',
      'Паспорт, РЭ (PDF)'
    ]
  },
  stapel: {
    name: 'Стапель сварочный 3х12 м',
    description: 'Комплект чертежей + 3D модель',
    zipUrl: 'https://disk.yandex.ru/d/Nv7iD6T5JYrKVQ/download',
    zipName: 'stapel.zip',
    contents: [
      'Чертежи КОМПАС (CDW)',
      '3D модели КОМПАС (A3D, M3D)',
      'Спецификации (SPW)'
    ]
  },
  level: {
    name: 'Уровнемер механический',
    description: 'Для любого емкостного без давления',
    zipUrl: 'https://disk.yandex.ru/d/79sH_E3uDXdNgw/download',
    zipName: 'level.zip',
    contents: [
      'Сборочный чертеж (CDW)',
      'Спецификация (PDF)',
      'Таблица сварных соединений',
      'Технические требования'
    ]
  }
};

// Настройка Mail.ru транспорта
const transporter = nodemailer.createTransport({
  host: 'smtp.mail.ru',
  port: 2525,
  secure: true,
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  }
});

// Функция генерации красивого HTML письма
function generateEmailHTML(product) {
  return `
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <style>
        body { 
          font-family: Arial, sans-serif; 
          line-height: 1.6; 
          color: #333; 
          margin: 0;
          padding: 0;
          background-color: #f5f5f5;
        }
        .container { 
          max-width: 600px; 
          margin: 20px auto; 
          background: white;
          border-radius: 10px;
          overflow: hidden;
          box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }
        .header { 
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
          color: white; 
          padding: 40px 20px; 
          text-align: center; 
        }
        .header h1 {
          margin: 0 0 10px 0;
          font-size: 32px;
        }
        .content { 
          padding: 40px 30px; 
        }
        .product-box {
          background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
          padding: 25px;
          border-radius: 10px;
          margin: 25px 0;
          border-left: 4px solid #667eea;
        }
        .product-box h2 {
          margin-top: 0;
          color: #667eea;
          font-size: 24px;
        }
        .download-section {
          background: white;
          padding: 30px;
          border-radius: 10px;
          margin: 25px 0;
          text-align: center;
          border: 2px dashed #667eea;
        }
        .download-button {
          display: inline-block;
          padding: 18px 50px;
          background: linear-gradient(45deg, #4CAF50, #45a049);
          color: white !important;
          text-decoration: none;
          border-radius: 8px;
          font-weight: bold;
          font-size: 18px;
          margin: 15px 0;
          box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
          transition: transform 0.2s;
        }
        .download-button:hover {
          transform: translateY(-2px);
        }
        .file-info {
          background: #f8f9fa;
          padding: 15px;
          border-radius: 8px;
          margin: 15px 0;
          font-size: 14px;
          color: #666;
        }
        .contents-list {
          text-align: left;
          margin: 15px 0;
          list-style: none;
          padding: 0;
        }
        .contents-list li {
          padding: 8px 0;
          border-bottom: 1px solid #e9ecef;
        }
        .contents-list li:last-child {
          border-bottom: none;
        }
        .contents-list li:before {
          content: "✅ ";
          margin-right: 8px;
        }
        .info-box {
          background: #fff3cd;
          border: 2px solid #ffc107;
          padding: 20px;
          border-radius: 8px;
          margin: 25px 0;
        }
        .info-box strong {
          color: #856404;
        }
        .footer { 
          text-align: center; 
          color: #666; 
          padding: 30px;
          background: #f8f9fa;
          border-top: 1px solid #e9ecef;
        }
        .footer a {
          color: #667eea;
          text-decoration: none;
          font-weight: bold;
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>✅ Спасибо за покупку!</h1>
          <p style="margin: 0; font-size: 16px; opacity: 0.95;">FIXCAD MARKET</p>
        </div>
        
        <div class="content">
          <p style="font-size: 18px; margin-bottom: 25px;">Здравствуйте!</p>
          
          <div class="product-box">
            <h2>${product.name}</h2>
            <p style="margin: 5px 0; color: #666; font-size: 16px;">${product.description}</p>
            <p style="margin: 15px 0 0 0; font-size: 14px;"><strong>Цена:</strong> 100 рублей</p>
          </div>
          
          <div class="download-section">
            <h3 style="margin-top: 0; color: #333;">📥 Ваш архив готов к скачиванию</h3>
            
            <div class="file-info">
              <strong>📦 ${product.zipName}</strong>
              <p style="margin: 5px 0 0 0;">Архив содержит все необходимые файлы</p>
            </div>
            
            <a href="${product.zipUrl}" class="download-button">
              ⬇️ СКАЧАТЬ АРХИВ
            </a>
            
            <p style="margin: 15px 0 0 0; font-size: 13px; color: #999;">
              Нажмите на кнопку для начала загрузки
            </p>
          </div>
          
          <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h4 style="margin-top: 0; color: #333;">📁 Содержимое архива:</h4>
            <ul class="contents-list">
              ${product.contents.map(item => `<li>${item}</li>`).join('')}
            </ul>
          </div>
          
          <div class="info-box">
            <strong>⚠️ Важная информация:</strong>
            <ul style="margin: 10px 0; padding-left: 20px;">
              <li>Ссылка действительна в течение 30 дней</li>
              <li>Скачайте архив и сохраните на своем устройстве</li>
              <li>Для открытия файлов КОМПАС требуется соответствующее ПО</li>
              <li>При возникновении проблем - свяжитесь с нами</li>
            </ul>
          </div>
          
          <div style="text-align: center; padding: 20px; background: #e7f3ff; border-radius: 8px;">
            <p style="margin: 0 0 10px 0; font-size: 16px;"><strong>💬 Нужна помощь?</strong></p>
            <p style="margin: 0;">
              Напишите нам: <a href="mailto:irashitov79@mail.ru" style="color: #667eea;">irashitov79@mail.ru</a>
            </p>
          </div>
        </div>
        
        <div class="footer">
          <p style="margin: 0 0 10px 0; font-size: 18px;"><strong>FIXCAD MARKET</strong></p>
          <p style="margin: 5px 0; color: #666;">Качественные чертежи и 3D-модели КОМПАС®</p>
          <p style="margin: 20px 0 5px 0; font-size: 14px;">
            <a href="mailto:irashitov79@mail.ru">irashitov79@mail.ru</a>
          </p>
        </div>
      </div>
    </body>
    </html>
  `;
}

// Webhook от ЮMoney - обрабатывает платежи
app.post('/webhook/yoomoney', async (req, res) => {
  try {
    const { label, withdraw_amount, notification_type, email } = req.body;
    
    console.log('📨 Получен webhook:', { label, email, amount: withdraw_amount });
    
    // Проверка типа уведомления
    if (notification_type !== 'p2p-incoming') {
      console.log('⏭️  Пропущено: не входящий платеж');
      return res.status(200).send('OK');
    }

    // Проверка суммы
    if (parseFloat(withdraw_amount) < 100) {
      console.log('⏭️  Пропущено: сумма меньше 100 руб');
      return res.status(200).send('OK');
    }

    const product = PRODUCTS[label];
    
    if (!product) {
      console.error('❌ Неизвестный товар:', label);
      return res.status(200).send('OK');
    }

    if (!email) {
      console.error('❌ Email не указан');
      return res.status(200).send('OK');
    }

    // Отправка email с архивом
    await transporter.sendMail({
      from: `"FIXCAD MARKET" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: `✅ Ваш заказ: ${product.name} - FIXCAD MARKET`,
      html: generateEmailHTML(product)
    });

    console.log(`✅ Email успешно отправлен на ${email} для товара ${label}`);
    res.status(200).send('OK');
    
  } catch (error) {
    console.error('❌ Ошибка обработки webhook:', error);
    res.status(500).send('Error');
  }
});

// Тестовый endpoint - отправит письмо вам на почту
app.get('/test-email', async (req, res) => {
  try {
    console.log('🔍 Начинаем тест отправки email...');
    console.log('📧 Email from:', process.env.EMAIL_USER);
    console.log('🔑 Password exists:', !!process.env.EMAIL_PASS);
    console.log('🔑 Password length:', process.env.EMAIL_PASS?.length || 0);
    
    const testProduct = PRODUCTS.stend;
    
    console.log('📤 Отправляем письмо...');
    await transporter.sendMail({
      from: `"FIXCAD MARKET" <${process.env.EMAIL_USER}>`,
      to: process.env.EMAIL_USER,
      subject: '🧪 ТЕСТ: Система работает!',
      html: generateEmailHTML(testProduct)
    });
    
    console.log('✅ Письмо успешно отправлено!');
    res.json({ 
      success: true, 
      message: 'Тестовое письмо отправлено на ' + process.env.EMAIL_USER 
    });
  } catch (error) {
    console.error('❌ ОШИБКА:', error.message);
    console.error('❌ Полная ошибка:', error);
    res.status(500).json({ 
      error: error.message,
      code: error.code,
      details: 'Проверьте настройки EMAIL_USER и EMAIL_PASS'
    });
  }
});

// Ручная отправка (для тестов и отладки)
app.post('/send-manual', async (req, res) => {
  try {
    const { email, productLabel } = req.body;
    
    if (!email || !productLabel) {
      return res.status(400).json({ 
        error: 'Параметры email и productLabel обязательны' 
      });
    }
    
    const product = PRODUCTS[productLabel];
    
    if (!product) {
      return res.status(404).json({ 
        error: 'Товар не найден',
        available: Object.keys(PRODUCTS)
      });
    }
    
    await transporter.sendMail({
      from: `"FIXCAD MARKET" <${process.env.EMAIL_USER}>`,
      to: email,
      subject: `Ваш заказ: ${product.name}`,
      html: generateEmailHTML(product)
    });
    
    res.json({ 
      success: true, 
      message: `Email отправлен на ${email}` 
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Информация о всех товарах
app.get('/products', (req, res) => {
  const productsList = Object.entries(PRODUCTS).map(([key, product]) => ({
    id: key,
    name: product.name,
    description: product.description,
    zipName: product.zipName
  }));
  
  res.json(productsList);
});

// Информация о конкретном товаре
app.get('/product/:label', (req, res) => {
  const product = PRODUCTS[req.params.label];
  if (product) {
    res.json({
      label: req.params.label,
      ...product
    });
  } else {
    res.status(404).json({ 
      error: 'Товар не найден',
      available: Object.keys(PRODUCTS)
    });
  }
});

// Главная страница - проверка статуса
app.get('/test', (req, res) => {
  res.json({ 
    status: '🚀 Сервер работает',
    email: process.env.EMAIL_USER ? '✅ настроен' : '❌ не настроен',
    products: Object.keys(PRODUCTS),
    endpoints: {
      'GET /test': 'Проверка статуса сервера',
      'GET /test-email': 'Отправка тестового письма себе',
      'GET /products': 'Список всех товаров',
      'GET /product/:label': 'Информация о товаре',
      'POST /webhook/yoomoney': 'Webhook от ЮMoney',
      'POST /send-manual': 'Ручная отправка (email, productLabel)'
    }
  });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`
╔════════════════════════════════════════╗
║     🚀 FIXCAD MARKET BACKEND          ║
╚════════════════════════════════════════╝
  
  📍 Порт: ${PORT}
  📧 Email: ${process.env.EMAIL_USER || '❌ НЕ НАСТРОЕН'}
  📦 Товары: ${Object.keys(PRODUCTS).join(', ')}
  
  Endpoints:
  • GET  /test         - проверка статуса
  • GET  /test-email   - тест отправки
  • GET  /products     - список товаров
  • POST /webhook/yoomoney - webhook от ЮMoney
  
╚════════════════════════════════════════╝
  `);

});
