(function ($) {
    'use strict';

    const STORAGE_KEY = 'patitasVetCart';

    function getCart() {
        try {
            const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
            return Array.isArray(value) ? value : [];
        } catch (_) {
            return [];
        }
    }

    function saveCart(cart) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
        updateCartCount();
        window.dispatchEvent(new CustomEvent('patitas:cart-updated', { detail: { cart } }));
    }

    function totalItems(cart = getCart()) {
        return cart.reduce((sum, item) => sum + Number(item.cantidad || 0), 0);
    }

    function updateCartCount() {
        const badge = document.getElementById('cart-count');
        if (!badge) return;
        const count = totalItems();
        badge.textContent = count;
        badge.hidden = count <= 0;
    }

    function formatMoney(value) {
        return new Intl.NumberFormat('es-AR', {
            style: 'currency',
            currency: 'ARS',
            maximumFractionDigits: 2
        }).format(Number(value || 0));
    }

    function normalizeProduct(data, stockUrl) {
        const product = data.producto || data.product || data;
        return {
            id: Number(product.id),
            nombre: product.nombre || product.name || 'Producto',
            precio: Number(product.precio || product.price || 0),
            imagen_url: product.imagen_url || product.image_url || '',
            stock: Number(product.stock || 0),
            cantidad: 1,
            detalle_url: product.detalle_url || product.detail_url || '#',
            stock_url: stockUrl
        };
    }

    function validateStock(stockUrl, quantity) {
        if (!stockUrl) return $.Deferred().reject({ message: 'No se encontró el endpoint de stock.' }).promise();
        return $.ajax({
            url: stockUrl,
            method: 'GET',
            dataType: 'json',
            data: { cantidad: quantity }
        });
    }

    function addProduct(button) {
        const $button = $(button);
        const productId = Number($button.data('product-id'));
        const stockUrl = String($button.data('stock-url') || '');
        const cart = getCart();
        const current = cart.find((item) => Number(item.id) === productId);
        const requestedQuantity = Number(current?.cantidad || 0) + 1;

        $button.prop('disabled', true).addClass('is-loading');
        validateStock(stockUrl, requestedQuantity)
            .done((data) => {
                if (data.ok === false) {
                    notify(data.mensaje || 'No hay stock suficiente.', 'warning');
                    return;
                }
                const incoming = normalizeProduct(data, stockUrl);
                if (current) {
                    current.cantidad = requestedQuantity;
                    current.stock = incoming.stock || current.stock;
                    current.precio = incoming.precio || current.precio;
                    current.stock_url = stockUrl || current.stock_url;
                } else {
                    incoming.cantidad = 1;
                    cart.push(incoming);
                }
                saveCart(cart);
                notify(data.mensaje || `${incoming.nombre} se agregó al carrito.`, 'success');
                renderCartPage();
            })
            .fail((xhr) => {
                const message = xhr.responseJSON?.mensaje || xhr.responseJSON?.detail || 'No pudimos validar el stock.';
                notify(message, 'danger');
            })
            .always(() => {
                $button.prop('disabled', false).removeClass('is-loading');
            });
    }

    function removeProduct(productId) {
        saveCart(getCart().filter((item) => Number(item.id) !== Number(productId)));
        renderCartPage();
        notify('Producto eliminado del carrito.', 'info');
    }

    function clearCart() {
        saveCart([]);
        renderCartPage();
        notify('Carrito vaciado.', 'info');
    }

    function changeQuantity(productId, quantity) {
        quantity = Number(quantity);
        if (quantity <= 0) {
            removeProduct(productId);
            return;
        }
        const cart = getCart();
        const item = cart.find((entry) => Number(entry.id) === Number(productId));
        if (!item) return;

        if (!item.stock_url) {
            if (quantity > Number(item.stock || 0)) {
                notify('No hay stock suficiente.', 'warning');
                return;
            }
            item.cantidad = quantity;
            saveCart(cart);
            renderCartPage();
            return;
        }

        validateStock(item.stock_url, quantity)
            .done((data) => {
                if (data.ok === false) {
                    notify(data.mensaje || 'No hay stock suficiente.', 'warning');
                    return;
                }
                item.cantidad = quantity;
                if (data.producto?.stock !== undefined) item.stock = Number(data.producto.stock);
                saveCart(cart);
                renderCartPage();
            })
            .fail((xhr) => notify(xhr.responseJSON?.mensaje || 'No pudimos validar el stock.', 'danger'));
    }

    function renderCartPage() {
        const root = document.getElementById('cart-page');
        if (!root) return;
        const cart = getCart();
        const esc = window.PatitasEscapeHtml || ((value) => String(value));

        if (!cart.length) {
            root.innerHTML = `
                <div class="empty-state">
                    <i class="bi bi-bag-heart"></i>
                    <h3>Tu carrito está vacío</h3>
                    <p>Explorá el catálogo y agregá productos para verlos acá.</p>
                    <a class="btn btn-primary-app" href="/catalogo/">Explorar catálogo</a>
                </div>`;
            return;
        }

        const subtotal = cart.reduce((sum, item) => sum + Number(item.precio || 0) * Number(item.cantidad || 0), 0);
        const itemsHtml = cart.map((item) => `
            <div class="cart-item" data-product-id="${Number(item.id)}">
                <div class="cart-item-media">
                    ${item.imagen_url ? `<img src="${esc(item.imagen_url)}" alt="${esc(item.nombre)}">` : '<div class="catalog-card-placeholder h-100"><i class="bi bi-bag-heart"></i></div>'}
                </div>
                <div class="cart-item-copy">
                    <a href="${esc(item.detalle_url || '#')}">${esc(item.nombre)}</a>
                    <small>${formatMoney(item.precio)} por unidad</small>
                    <button class="btn btn-link btn-sm text-danger p-0 mt-2 js-cart-remove" data-product-id="${Number(item.id)}">Quitar</button>
                </div>
                <div class="cart-quantity" aria-label="Cantidad">
                    <button type="button" class="js-cart-qty" data-product-id="${Number(item.id)}" data-quantity="${Number(item.cantidad) - 1}" aria-label="Restar"><i class="bi bi-dash"></i></button>
                    <span>${Number(item.cantidad)}</span>
                    <button type="button" class="js-cart-qty" data-product-id="${Number(item.id)}" data-quantity="${Number(item.cantidad) + 1}" aria-label="Sumar"><i class="bi bi-plus"></i></button>
                </div>
                <div class="cart-item-subtotal">${formatMoney(Number(item.precio) * Number(item.cantidad))}</div>
            </div>`).join('');

        root.innerHTML = `
            <div class="cart-layout">
                <div class="cart-list">${itemsHtml}</div>
                <aside class="cart-summary">
                    <h2>Resumen</h2>
                    <div class="cart-summary-row"><span>Productos</span><strong>${totalItems(cart)}</strong></div>
                    <div class="cart-summary-total"><span>Total</span><span>${formatMoney(subtotal)}</span></div>
                    <p class="small text-muted">El stock se valida al modificar cantidades. El checkout puede incorporarse como siguiente etapa.</p>
                    <button type="button" class="btn btn-outline-danger w-100 js-cart-clear"><i class="bi bi-trash3"></i> Vaciar carrito</button>
                </aside>
            </div>`;
    }

    function notify(message, type) {
        if (window.PatitasUI?.toast) window.PatitasUI.toast(message, type);
        const feedback = document.getElementById('cart-feedback');
        if (feedback) {
            feedback.innerHTML = `<div class="alert alert-${type === 'danger' ? 'danger' : type === 'warning' ? 'warning' : 'success'} mb-0">${window.PatitasEscapeHtml ? window.PatitasEscapeHtml(message) : message}</div>`;
        }
    }

    $(document)
        .on('click', '.js-add-to-cart', function (event) { event.preventDefault(); addProduct(this); })
        .on('click', '.js-cart-remove', function () { removeProduct($(this).data('product-id')); })
        .on('click', '.js-cart-clear', clearCart)
        .on('click', '.js-cart-qty', function () { changeQuantity($(this).data('product-id'), $(this).data('quantity')); });

    $(function () {
        updateCartCount();
        renderCartPage();
    });

    window.PatitasCart = { getCart, saveCart, updateCartCount, addProduct, removeProduct, clearCart, changeQuantity, renderCartPage, formatMoney };
})(jQuery);
