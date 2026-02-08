// products.js

// Данные товаров для генерации карточек и микроразметки
const PRODUCTS_DATA = {
    RalColorPro: {
        name: "Утилита для раскраски моделей КОМПАС-3D по цветам RAL",
        description: "Выделяйте объекты в модели, выбирайте цвет из палитры — и мгновенно применяйте его",
        image: "images/RalColorPro.png",
        model: null,
        formatBadge: "EXE",
        formats: ["EXE", "TXT"],
        features: ["Все цвета стандарта RAL", "Точность цветопередачи", "Простота использования"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=RalColorPro'
    },
    stend: {
        name: "Стенд для сборки-разборки пакерно-якорного оборудования",
        description: "Полный комплект чертежей, 3D моделей и эксплуатационной документации",
        image: "images/stend.png",
        model: "models/stend.stl",
        formatBadge: "STL",
        formats: ["CDW", "SPW", "A3D", "M3D"],
        features: ["Чертежи КОМПАС v18.1", "3D модели КОМПАС v18.1", "Паспорт, РЭ"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=stend'
    },
    stapel: {
        name: "Стапель сварочный 3х12 м",
        description: "Комплект чертежей + 3D модель: файлы в версии Компас 18.1",
        image: "images/stapel.png",
        model: "models/stapel.stl",
        formatBadge: "STL",
        formats: ["CDW", "SPW", "A3D", "M3D"],
        features: ["Чертежи КОМПАС", "3D модели КОМПАС", "Спецификации"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=stapel'
    },
    vent: {
        name: "Вентилятор ВР-80-75-2,5 взрывозащищенный",
        description: "Сборочный чертеж, 3D модель Компас v21",
        image: "images/vent.png",
        model: "models/vent.stl",
        formatBadge: "STL",
        formats: ["M3D", "STL", "STEP", "TXT"],
        features: ["Сборочный чертеж JPG", "3D модель КОМПАС", "Видеоинструкция по изготовлению", "Файл STEP"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=vent'
    },
    level: {
        name: "Уровнемер механический поплавковый",
        description: "Для любого емкостного оборудования без давления. Версия Компас 18.1",
        image: "images/level.png",
        model: null,
        formatBadge: "CDW",
        formats: ["CDW", "TXT"],
        features: ["Сборочный чертеж", "Спецификация", "Таблица сварных соединений", "Технические требования"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=level'
    },
    freza: {
        name: "Торцевая фреза с механическим креплением сменных многогранных пластин (СМП)",
        description: "3D модель: файлы в версии Компас 21",
        image: "images/freza.png",
        model: "models/freza.stl",
        formatBadge: "STL",
        formats: ["A3D", "M3D", "TXT"],
        features: ["3D модели КОМПАС", "Описание"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=freza'
    },
    apidomik: {
        name: "Апидомик на 8 ульев 3х5 м (павильон для апитерапии)",
        description: "Чертеж Компас 18.1 и модель STEP",
        image: "images/apidomik.png",
        model: "models/apidomik.stl",
        formatBadge: "STL",
        formats: ["CDW", "STP"],
        features: ["Габаритный чертеж", "Файл STEP", "Полная детализация", "Ульи с рамками"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=apidomik'
    },
    vanna: {
        name: "Моечная ванна для технологической очистки оборудования",
        description: "Стальная сварная емкость со столом и сливным краном",
        image: "images/vanna.png",
        model: "models/vanna.stl",
        formatBadge: "STL",
        formats: ["STP", "DOCX", "TXT"],
        features: ["Полноценная 3D-модель STEP", "Полная деталировка", "Паспорт", "Руководство по эксплуатации"],
        paymentUrl: 'https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label=vanna'
    }
};

// Функция для генерации HTML карточек товаров
function generateProductsHTML() {
    const productsGrid = document.querySelector('.products-grid');
    if (!productsGrid) return;
    
    let html = '';
    
    for (const [productId, product] of Object.entries(PRODUCTS_DATA)) {
        const hasModel = product.model !== null;
        
        html += `
        <div class="product-card">
            <div class="product-image" data-image="${product.image}" ${hasModel ? `data-model="${product.model}"` : ''} tabindex="0" role="button" aria-label="Просмотр ${product.name}">
                <img src="${product.image}" alt="${product.name}" loading="lazy">
                <div class="format-badge">${product.formatBadge}</div>
                <div class="model-indicator">${hasModel ? '3D просмотр' : 'Изображение'}</div>
            </div>
            <div class="product-title">${product.name}</div>
            <div class="product-description">${product.description}</div>
            <div class="formats-list">
                ${product.formats.map(format => `<span class="format-tag">${format}</span>`).join('')}
            </div>
            <ul class="product-features">
                ${product.features.map(feature => `<li>${feature}</li>`).join('')}
            </ul>
            <button class="buy-button" data-product="${productId}" aria-label="Скачать ${product.name} за 100 рублей">
                Скачать за 100 руб.
            </button>
        </div>
        `;
    }
    
    productsGrid.innerHTML = html;
}

// Функция для генерации данных для микроразметки
function generateProductStructuredData() {
    const productsData = [];
    
    for (const [productId, product] of Object.entries(PRODUCTS_DATA)) {
        const productMarkup = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": product.name,
            "description": product.description,
            "image": `https://fixcad.ru/${product.image}`,
            "offers": {
                "@type": "Offer",
                "price": "100",
                "priceCurrency": "RUB",
                "availability": "https://schema.org/InStock"
            },
            "brand": {
                "@type": "Brand",
                "name": "FIXCAD MARKET"
            }
        };
        productsData.push(productMarkup);
    }
    
    return productsData;
}

// Функция для получения URL оплаты
function getPaymentUrl(productId) {
    return PRODUCTS_DATA[productId]?.paymentUrl || '';
}

// Функция для получения названия товара
function getProductName(productId) {
    return PRODUCTS_DATA[productId]?.name || '';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    generateProductsHTML();
    
    // Добавляем микроразметку
    const productsData = generateProductStructuredData();
    productsData.forEach(markup => {
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(markup);
        document.head.appendChild(script);
    });
});
