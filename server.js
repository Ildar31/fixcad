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
    name: 'Стенд для сборки-разборки пакерно-якорного оборудования',
    description: 'Полный комплект чертежей, 3D моделей и эксплуатационной документации',
    zipUrl: 'https://disk.yandex.ru/d/yavUz8k9ce2gAw/download',
    zipName: 'stend.zip',
    contents: ["Чертежи КОМПАС v18.1", "3D модели КОМПАС v18.1", "Паспорт, РЭ"]
  },
  stapel: {
    name: 'Стапель сварочный 3х12 м',
    description: 'Комплект чертежей + 3D модель: файлы в версии Компас 18.1',
    zipUrl: 'https://disk.yandex.ru/d/Nv7iD6T5JYrKVQ/download',
    zipName: 'stapel.zip',
    contents: ["Чертежи КОМПАС", "3D модели КОМПАС", "Спецификации"]
  },
  vent: {
    name: 'Вентилятор ВР-80-75-2,5 взрывозащищенный',
    description: 'Сборочный чертеж, 3D модель Компас v21',
    zipUrl: 'https://disk.yandex.ru/d/VV65Q1zBSR9D0Q/download',
    zipName: 'vent.zip',
    contents: ["Сборочный чертеж JPG", "3D модель КОМПАС", "Видеоинструкция по изготовлению", "Файл STEP"]
  },
  level: {
    name: 'Уровнемер механический поплавковый',
    description: 'Для любого емкостного оборудования без давления. Версия Компас 18.1',
    zipUrl: 'https://disk.yandex.ru/d/79sH_E3uDXdNgw/download',
    zipName: 'level.zip',
    contents: ["Сборочный чертеж", "Спецификация", "Таблица сварных соединений", "Технические требования"]
  },
  freza: {
    name: 'Торцевая фреза с механическим креплением сменных многогранных пластин (СМП)',
    description: '3D модель: файлы в версии Компас 21',
    zipUrl: 'https://disk.yandex.ru/d/Vzko94j5NanGMg/download',
    zipName: 'freza.zip',
    contents: ["3D модели КОМПАС", "Описание"]
  },
  apidomik: {
    name: 'Апидомик на 8 ульев 3х5 м (павильон для апитерапии)',
    description: 'Чертеж Компас 18.1 и модель STEP',
    zipUrl: 'https://disk.yandex.ru/d/x-xoLOFzicx3uQ/download',
    zipName: 'apidomik.zip',
    contents: ["Габаритный чертеж", "Файл STEP", "Полная детализация", "Ульи с рамками"]
  }
};
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;
;

// Настройка Mail.ru транспорта
const transporter = nodemailer.createTransport({
  host: 'smtp.mail.ru',
  port: 2525,
  secure: false, // Без SSL
  auth: {
    user: process.env.EMAIL_USER,
    pass: process.env.EMAIL_PASS
  },
  tls: {
    rejectUnauthorized: false // Игнорировать ошибки сертификата
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

// Endpoint для обработки заказов (без отправки ссылки покупателю)
app.post('/api/order', async (req, res) => {
  try {
    const { product, name, email, phone, comment } = req.body;
    
    console.log('📦 Получен новый заказ:', { product, name, email });
    
    if (!product || !name || !email) {
      return res.status(400).json({ 
        error: 'Необходимо указать product, name и email' 
      });
    }

    const productInfo = PRODUCTS[product];
    if (!productInfo) {
      return res.status(404).json({ 
        error: 'Товар не найден',
        available: Object.keys(PRODUCTS)
      });
    }

    // Отправляем уведомление вам на почту о новом заказе
    const orderHTML = `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="UTF-8">
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }
          .order-details { background: white; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #667eea; }
          .customer-info { background: white; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #28a745; }
          .payment-info { background: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ffc107; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🛒 Новый заказ FIXCAD MARKET</h1>
            <p>Ожидает оплаты</p>
          </div>
          <div class="content">
            <div class="order-details">
              <h3>📦 Информация о заказе</h3>
              <p><strong>Товар:</strong> ${productInfo.name}</p>
              <p><strong>Архив:</strong> ${productInfo.zipName}</p>
              <p><strong>Цена:</strong> 100 руб.</p>
              <p><strong>Время:</strong> ${new Date().toLocaleString('ru-RU')}</p>
            </div>
            
            <div class="customer-info">
              <h3>👤 Данные покупателя</h3>
              <p><strong>ФИО:</strong> ${name}</p>
              <p><strong>Email:</strong> ${email}</p>
              <p><strong>Телефон:</strong> ${phone || 'Не указан'}</p>
              <p><strong>Комментарий:</strong> ${comment || 'Нет комментария'}</p>
            </div>

            <div class="payment-info">
              <h3>💳 Статус оплаты</h3>
              <p><strong>⚠️ ОЖИДАЕТ ОПЛАТЫ</strong></p>
              <p>Ссылка для скачивания будет отправлена автоматически после подтверждения оплаты через ЮMoney.</p>
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
              <p><strong>Ссылка для скачивания (после оплаты):</strong></p>
              <a href="${productInfo.zipUrl}" style="color: #667eea; word-break: break-all;">${productInfo.zipUrl}</a>
            </div>
          </div>
        </div>
      </body>
      </html>
    `;

    // Отправляем письмо только вам (администратору)
    await transporter.sendMail({
      from: `"FIXCAD MARKET - Заказы" <${process.env.EMAIL_USER}>`,
      to: process.env.EMAIL_USER, // Письмо приходит только вам
      subject: `🛒 Новый заказ (ожидает оплаты): ${productInfo.name}`,
      html: orderHTML
    });

    console.log(`✅ Уведомление о новом заказе отправлено вам на ${process.env.EMAIL_USER}`);

    res.json({ 
      success: true, 
      message: 'Данные заказа отправлены. Переход к оплате...',
      orderId: Date.now()
    });
    
  } catch (error) {
    console.error('❌ Ошибка обработки заказа:', error);
    res.status(500).json({ 
      error: 'Ошибка сервера при обработке заказа',
      details: error.message 
    });
  }
});

// Webhook от ЮMoney - обрабатывает платежи и отправляет ссылку покупателю
app.post('/webhook/yoomoney', async (req, res) => {
  try {
    const { label, withdraw_amount, notification_type } = req.body;
    
    console.log('📨 Получен webhook от ЮMoney:', { 
      label, 
      amount: withdraw_amount,
      notification_type
    });
    
    // Обработка тестового уведомления от ЮMoney
    if (!label || label === '' || label === 'test') {
      console.log('✅ Тестовое уведомление от ЮMoney получено успешно');
      return res.status(200).json({ 
        status: 'OK', 
        message: 'Webhook работает корректно',
        received: req.body
      });
    }
    
    // ПРОВЕРКА ТИПА УВЕДОМЛЕНИЯ - принимаем ВСЕ входящие платежи
    if (!notification_type.includes('incoming')) {
      console.log('⏭️  Пропущено: не входящий платеж', notification_type);
      return res.status(200).send('OK');
    }

    // Ищем email в label (формат: product_email)
    let product, customerEmail;
    
    if (label.includes('_')) {
      const parts = label.split('_');
      product = parts[0]; // Первая часть - товар
      customerEmail = decodeURIComponent(parts.slice(1).join('_')); // Остальное - email
    } else {
      // Старый формат без email
      product = label;
      customerEmail = '';
    }

    const productInfo = PRODUCTS[product];
    
    if (!productInfo) {
      console.error('❌ Неизвестный товар:', product);
      return res.status(200).send('OK');
    }

    // Валидация email - ОСЛАБЛЕННАЯ проверка (всегда отправляем, но с предупреждением)
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    function isSuspiciousEmail(email) {
        // Подозрительные email - проходят базовую валидацию, но домен непопулярный
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) return false;
        
        // Проверяем популярные домены
        const popularDomains = [
            'gmail.com', 'yandex.ru', 'mail.ru', 'rambler.ru', 'yahoo.com',
            'outlook.com', 'hotmail.com', 'icloud.com', 'protonmail.com'
        ];
        
        const domain = email.split('@')[1];
        const hasPopularDomain = popularDomains.some(popular => 
            domain === popular || domain.endsWith('.' + popular)
        );
        
        return !hasPopularDomain;
    }

    let emailStatus = 'valid';
    if (!customerEmail) {
        emailStatus = 'missing';
    } else if (!isValidEmail(customerEmail)) {
        emailStatus = 'invalid';
    } else if (isSuspiciousEmail(customerEmail)) {
        emailStatus = 'suspicious';
    }

    // ОТПРАВЛЯЕМ письмо со ссылкой для скачивания покупателю В ЛЮБОМ СЛУЧАЕ
    if (customerEmail && isValidEmail(customerEmail)) {
        try {
            await transporter.sendMail({
                from: `"FIXCAD MARKET" <${process.env.EMAIL_USER}>`,
                to: customerEmail,
                subject: `✅ Оплата получена! Ваш заказ: ${productInfo.name} - FIXCAD MARKET`,
                html: generateEmailHTML(productInfo)
            });
            console.log(`✅ Письмо со ссылкой отправлено покупателю на ${customerEmail}`);
        } catch (emailError) {
            console.error('❌ Ошибка отправки письма покупателю:', emailError.message);
            emailStatus = 'sending_failed';
        }
    }

    // Всегда отправляем уведомление о получении платежа
    let adminSubject = `💳 Оплата получена: ${productInfo.name}`;
    let warningHtml = '';
    
    if (emailStatus !== 'valid') {
        if (emailStatus === 'suspicious') {
            adminSubject = `⚠️ Подозрительный email: ${productInfo.name}`;
            warningHtml = `
                <div style="background: #fff3cd; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h4 style="color: #856404; margin-top: 0;">⚠️ Внимание!</h4>
                    <p style="color: #856404; margin: 0;">
                        Email покупателя прошел базовую проверку, но домен непопулярный. 
                        Письмо отправлено, но рекомендуется проверить доставку.
                    </p>
                </div>
            `;
        } else if (emailStatus === 'invalid') {
            adminSubject = `❌ Неверный email: ${productInfo.name}`;
            warningHtml = `
                <div style="background: #f8d7da; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #dc3545;">
                    <h4 style="color: #721c24; margin-top: 0;">❌ Критическая проблема!</h4>
                    <p style="color: #721c24; margin: 0;">
                        Email покупателя неверный. Письмо НЕ отправлено!
                        Свяжитесь с покупателем для отправки файла вручную.
                    </p>
                </div>
            `;
        } else if (emailStatus === 'missing') {
            adminSubject = `❌ Отсутствует email: ${productInfo.name}`;
            warningHtml = `
                <div style="background: #f8d7da; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #dc3545;">
                    <h4 style="color: #721c24; margin-top: 0;">❌ Критическая проблема!</h4>
                    <p style="color: #721c24; margin: 0;">
                        Email покупателя отсутствует. Письмо НЕ отправлено!
                        Свяжитесь с покупателем для отправки файла вручную.
                    </p>
                </div>
            `;
        } else if (emailStatus === 'sending_failed') {
            adminSubject = `❌ Ошибка отправки: ${productInfo.name}`;
            warningHtml = `
                <div style="background: #f8d7da; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #dc3545;">
                    <h4 style="color: #721c24; margin-top: 0;">❌ Ошибка отправки!</h4>
                    <p style="color: #721c24; margin: 0;">
                        Не удалось отправить письмо покупателю. 
                        Свяжитесь с покупателем для отправки файла вручную.
                    </p>
                </div>
            `;
        }
    }

    await transporter.sendMail({
        from: `"FIXCAD MARKET - Платежи" <${process.env.EMAIL_USER}>`,
        to: process.env.EMAIL_USER,
        subject: adminSubject,
        html: `
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; font-family: Arial, sans-serif;">
                <div style="background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1>💳 Оплата получена!</h1>
                </div>
                <div style="background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px;">
                    <div style="background: white; padding: 15px; margin: 15px 0; border-radius: 8px;">
                        <h3>✅ Платеж подтвержден</h3>
                        <p><strong>Товар:</strong> ${productInfo.name}</p>
                        <p><strong>Покупатель:</strong> ${customerEmail || 'не указан'}</p>
                        <p><strong>Статус email:</strong> ${emailStatus === 'valid' ? '✅ Валидный' : emailStatus === 'suspicious' ? '⚠️ Подозрительный' : '❌ Проблемный'}</p>
                        <p><strong>Сумма:</strong> ${withdraw_amount} руб.</p>
                        <p><strong>Тип платежа:</strong> ${notification_type}</p>
                        <p><strong>Время:</strong> ${new Date().toLocaleString('ru-RU')}</p>
                    </div>
                    ${warningHtml}
                    ${emailStatus === 'valid' ? `
                    <p style="text-align: center; color: #666;">
                        Ссылка для скачивания отправлена покупателю автоматически.
                    </p>
                    ` : ''}
                    <div style="background: #e7f3ff; padding: 15px; margin: 15px 0; border-radius: 8px;">
                        <p style="margin: 0; color: #0066cc;"><strong>Ссылка для скачивания:</strong></p>
                        <p style="margin: 5px 0 0 0;"><a href="${productInfo.zipUrl}" style="color: #667eea; word-break: break-all;">${productInfo.zipUrl}</a></p>
                    </div>
                </div>
            </div>
        `
    });

    console.log(`✅ Уведомление об оплате отправлено вам`);

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
      'POST /api/order': 'НОВЫЙ: Оформление заказа',
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
  • POST /api/order    - оформление заказа
  • POST /webhook/yoomoney - webhook от ЮMoney
  
╚════════════════════════════════════════╝
  `);

});