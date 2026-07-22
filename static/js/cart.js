(function ($) {
    "use strict";

    const STORAGE_KEY = "patitasVetCart";

    function getCart() {
        try {
            const value = JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
            return Array.isArray(value) ? value.filter((item) => item && Number(item.id)) : [];
        } catch (error) {
            return [];
        }
    }

    function saveCart(cart) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
        updateCartCount();
    }

    function getCartTotalItems() {
        return getCart().reduce((total, item) => total + (Number(item.cantidad) || 0), 0);
    }

    function updateCartCount() {
        $("#cart-count").text(getCartTotalItems());
    }

    function stockUrl(productId) {
        const template = document.body.dataset.stockUrlTemplate || "/ajax/producto/0/validar-stock/";
        return template.replace(/\/0\//, `/${productId}/`);
    }

    function validateStock(productId, cantidad) {
        return $.ajax({
            url: stockUrl(productId),
            method: "GET",
            dataType: "json",
            data: { cantidad: cantidad }
        }).catch((xhr) => {
            const response = xhr.responseJSON || {};
            return $.Deferred().reject({
                mensaje: response.mensaje || "No pudimos validar el stock. Intentá nuevamente."
            }).promise();
        });
    }

    function showFeedback(message, type) {
        let $feedback = $("#cart-feedback").first();
        if (!$feedback.length) {
            $feedback = $("<div>", {
                id: "global-cart-feedback",
                class: "cart-floating-feedback",
                "aria-live": "polite"
            }).appendTo(document.body);
        }
        $feedback.html(
            $("<div>", {
                class: `alert alert-${type || "success"} alert-dismissible fade show`,
                role: "alert",
                text: message
            }).append($("<button>", {
                type: "button",
                class: "btn-close",
                "data-bs-dismiss": "alert",
                "aria-label": "Cerrar"
            }))
        );
    }

    function addProductToCart(productId) {
        const cart = getCart();
        const existing = cart.find((item) => Number(item.id) === Number(productId));
        const requestedQuantity = existing ? Number(existing.cantidad) + 1 : 1;

        return validateStock(productId, requestedQuantity).then((data) => {
            if (!data.ok) {
                showFeedback(data.mensaje, "warning");
                return false;
            }
            if (existing) {
                existing.cantidad = requestedQuantity;
                existing.stock = data.producto.stock;
            } else {
                cart.push({
                    id: data.producto.id,
                    nombre: data.producto.nombre,
                    precio: Number(data.producto.precio),
                    imagen_url: data.producto.imagen_url,
                    stock: data.producto.stock,
                    cantidad: 1,
                    detalle_url: data.producto.detalle_url
                });
            }
            saveCart(cart);
            showFeedback(`${data.producto.nombre} se agregó al carrito.`, "success");
            renderCartPage();
            return true;
        }).catch((error) => {
            showFeedback(error.mensaje || "No pudimos agregar el producto.", "danger");
            return false;
        });
    }

    function removeProductFromCart(productId) {
        const cart = getCart().filter((item) => Number(item.id) !== Number(productId));
        saveCart(cart);
        showFeedback("Producto quitado del carrito.", "success");
        renderCartPage();
    }

    function clearCart() {
        saveCart([]);
        showFeedback("Vaciaste el carrito.", "success");
        renderCartPage();
    }

    function changeProductQuantity(productId, newQuantity) {
        if (newQuantity < 1) {
            removeProductFromCart(productId);
            return $.Deferred().resolve().promise();
        }
        return validateStock(productId, newQuantity).then((data) => {
            if (!data.ok) {
                showFeedback(data.mensaje, "warning");
                renderCartPage();
                return;
            }
            const cart = getCart();
            const item = cart.find((entry) => Number(entry.id) === Number(productId));
            if (item) {
                item.cantidad = newQuantity;
                item.stock = data.producto.stock;
                item.precio = Number(data.producto.precio);
                saveCart(cart);
                renderCartPage();
            }
        }).catch((error) => {
            showFeedback(error.mensaje || "No pudimos actualizar la cantidad.", "danger");
            renderCartPage();
        });
    }

    function formatMoney(value) {
        return new Intl.NumberFormat("es-AR", {
            style: "currency",
            currency: "ARS",
            minimumFractionDigits: 2
        }).format(Number(value) || 0);
    }

    function escapeHtml(value) {
        return $("<div>").text(value == null ? "" : String(value)).html();
    }

    function renderCartPage() {
        const $page = $("#cart-page");
        if (!$page.length) return;
        const cart = getCart();
        if (!cart.length) {
            $page.html('<div class="text-center border rounded p-5 bg-light"><i class="bi bi-cart3 display-5 text-secondary"></i><h2 class="h4 mt-3">Tu carrito está vacío</h2><p class="text-muted mb-0">Agregá productos desde el catálogo.</p></div>');
            return;
        }

        let total = 0;
        const rows = cart.map((item) => {
            const subtotal = Number(item.precio) * Number(item.cantidad);
            total += subtotal;
            const image = item.imagen_url
                ? `<img src="${escapeHtml(item.imagen_url)}" alt="" class="cart-product-image rounded">`
                : '<span class="cart-product-image rounded bg-light d-inline-flex align-items-center justify-content-center"><i class="bi bi-image"></i></span>';
            return `<tr>
                <td>${image}</td>
                <td><a href="${escapeHtml(item.detalle_url)}" class="fw-semibold text-decoration-none">${escapeHtml(item.nombre)}</a></td>
                <td>${formatMoney(item.precio)}</td>
                <td><input type="number" class="form-control form-control-sm cart-quantity" min="1" max="${Number(item.stock) || 1}" value="${Number(item.cantidad)}" data-product-id="${Number(item.id)}" aria-label="Cantidad de ${escapeHtml(item.nombre)}"></td>
                <td class="fw-semibold">${formatMoney(subtotal)}</td>
                <td><button type="button" class="btn btn-outline-danger btn-sm js-remove-cart-item" data-product-id="${Number(item.id)}" aria-label="Quitar ${escapeHtml(item.nombre)}"><i class="bi bi-trash"></i></button></td>
            </tr>`;
        }).join("");

        $page.html(`<div class="table-responsive"><table class="table align-middle cart-table">
            <thead><tr><th scope="col">Imagen</th><th scope="col">Producto</th><th scope="col">Precio</th><th scope="col">Cantidad</th><th scope="col">Subtotal</th><th scope="col"></th></tr></thead>
            <tbody>${rows}</tbody></table></div>
            <div class="d-flex flex-wrap justify-content-between align-items-center gap-3 mt-4">
                <button type="button" class="btn btn-outline-danger" id="clear-cart"><i class="bi bi-trash"></i> Vaciar carrito</button>
                <p class="fs-4 fw-bold mb-0">Total: <span class="text-success">${formatMoney(total)}</span></p>
            </div>`);
    }

    $(document).on("click", ".js-add-to-cart", function (event) {
        event.preventDefault();
        const $button = $(this);
        $button.prop("disabled", true);
        addProductToCart($button.data("product-id")).always(() => $button.prop("disabled", false));
    });
    $(document).on("click", ".js-remove-cart-item", function () {
        removeProductFromCart($(this).data("product-id"));
    });
    $(document).on("click", "#clear-cart", clearCart);
    $(document).on("change", ".cart-quantity", function () {
        changeProductQuantity($(this).data("product-id"), Number($(this).val()));
    });

    $(function () {
        updateCartCount();
        renderCartPage();
    });

    window.PatitasVetCart = {
        getCart, saveCart, getCartTotalItems, updateCartCount, validateStock,
        addProductToCart, removeProductFromCart, clearCart,
        changeProductQuantity, renderCartPage, formatMoney
    };
})(jQuery);
