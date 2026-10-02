(function ($) {
    'use strict';
    const success = document.querySelector('[data-clear-cart]');
    if (success) {
        if (success.dataset.clearCart === 'true') window.PatitasCart?.saveCart([]);
        return;
    }
    const form = document.getElementById('checkout-form');
    if (!form) return;
    const cart = window.PatitasCart;
    const panels = [...document.querySelectorAll('.checkout-step-panel')];
    const $form = $(form);
    let step = 0;
    let draftTimer;
    const money = value => cart.formatMoney(value);
    const field = name => form.elements.namedItem(name);
    const selected = name => $form.find(`[name="${name}"]:checked`).val() || '';

    function conditionals(showModal = false) {
        const especial = document.getElementById('solicitar-factura-especial').checked;
        let opcion = selected('factura_especial_opcion');
        if (especial && !opcion) {
            const facturaA = $form.find('[name="factura_especial_opcion"][value="A"]');
            facturaA.prop('checked', true);
            opcion = 'A';
        }
        field('tipo_factura').value = especial ? opcion : 'B';
        const factura = field('tipo_factura').value;
        const mismos = field('facturacion_mismos_datos').checked;
        $('#factura-especial-opciones').prop('hidden', !especial);
        $('#factura-b-fields').prop('hidden', factura !== 'B');
        $('#factura-b-otros').prop('hidden', factura !== 'B' || mismos);
        $('#factura-ae-fields').prop('hidden', factura === 'B');
        $('#factura-pais').prop('hidden', factura !== 'E');
        $('#factura-domicilio').prop('hidden', factura === 'B' && mismos);
        $('#retiro-fields').prop('hidden', selected('tipo_entrega') !== 'retiro');
        $('#envio-fields').prop('hidden', selected('tipo_entrega') !== 'envio');
        $('#destinatario-heading').text(selected('tipo_entrega') === 'retiro' ? 'Persona que retira' : selected('tipo_entrega') === 'envio' ? 'Persona que recibe' : 'Persona que recibe o retira');
        $('#receptor-otros').prop('hidden', field('receptor_mismos_datos').checked);
        const transferencia = selected('medio_pago') === 'transferencia';
        $('#transferencia-fields').prop('hidden', !transferencia);
        if (transferencia && showModal) {
            const modal = document.getElementById('transferencia-modal');
            if (modal) bootstrap.Modal.getOrCreateInstance(modal).show();
        }
        renderSummary();
    }

    function renderSummary() {
        const items = cart.getCart();
        const esc = window.PatitasEscapeHtml || (value => String(value));
        $('#checkout-items').html(items.length ? items.map(item => `<div class="checkout-summary-item">${item.imagen_url ? `<img src="${esc(item.imagen_url)}" alt="" class="checkout-summary-thumb">` : '<span class="checkout-summary-thumb"><i class="bi bi-bag-heart"></i></span>'}<span class="flex-grow-1">${esc(item.nombre)}<small class="d-block text-muted">${Number(item.cantidad)} × ${money(item.precio)}</small></span><strong>${money(Number(item.precio) * Number(item.cantidad))}</strong></div>`).join('') : '<p>Tu carrito está vacío.</p>');
        const subtotal = items.reduce((sum, item) => sum + Number(item.precio || 0) * Number(item.cantidad || 0), 0);
        const threshold = form.dataset.freeThreshold === '' ? null : Number(form.dataset.freeThreshold);
        const entrega = selected('tipo_entrega');
        const shipping = entrega === 'envio' && (threshold === null || subtotal < threshold) ? Number(form.dataset.shipping) : 0;
        $('#checkout-count').text(items.reduce((sum, item) => sum + Number(item.cantidad || 0), 0));
        $('#checkout-subtotal').text(money(subtotal));
        $('#checkout-shipping').text(entrega ? money(shipping) : 'Por definir');
        $('#checkout-total').text(entrega ? money(subtotal + shipping) : 'Por definir');
        field('cart_payload').value = JSON.stringify(items.map(item => ({ id: Number(item.id), cantidad: Number(item.cantidad) })));
        $('#checkout-submit').prop('disabled', !items.length);
    }

    function showStep(index) {
        step = Math.max(0, Math.min(index, panels.length - 1));
        panels.forEach((panel, i) => { panel.hidden = i !== step; });
        $('#checkout-back').prop('hidden', step === 0);
        $('#checkout-next').prop('hidden', step === panels.length - 1);
        $('#checkout-submit').prop('hidden', step !== panels.length - 1);
        $('#checkout-progress-fill').css('width', `${(step + 1) / panels.length * 100}%`);
        $('.checkout-steps span').each(function (i) { $(this).toggleClass('active', i === step).toggleClass('complete', i < step); });
        panels[step].scrollIntoView({ behavior: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block: 'start' });
    }

    function validStep() {
        const factura = field('tipo_factura').value;
        const entrega = selected('tipo_entrega');
        const names = [
            ['comprador_nombre', 'comprador_apellido', 'comprador_email', 'comprador_telefono', 'comprador_dni'].concat(
                factura === 'B' ? (field('facturacion_mismos_datos').checked ? [] : ['facturacion_nombre', 'facturacion_apellido', 'facturacion_dni', 'facturacion_domicilio']) : ['facturacion_cuit', 'facturacion_razon_social', 'facturacion_domicilio', 'facturacion_condicion_iva'].concat(factura === 'E' ? ['facturacion_pais'] : [])
            ),
            (entrega === 'envio' ? ['envio_calle', 'envio_altura', 'envio_localidad', 'envio_provincia', 'envio_codigo_postal'] : []).concat(
                field('receptor_mismos_datos').checked ? [] : ['receptor_nombre', 'receptor_apellido', 'receptor_dni', 'receptor_telefono']
            ),
            selected('medio_pago') === 'transferencia' ? ['comprobante'] : [], []
        ][step];
        if (step === 1 && !entrega) { alertInline('Elegí una forma de entrega.'); return false; }
        if (step === 2 && !selected('medio_pago')) { alertInline('Elegí un medio de pago.'); return false; }
        for (const name of names) {
            const input = field(name);
            if (!input?.value?.trim()) { input?.focus(); alertInline('Completá los campos obligatorios de este paso.'); return false; }
            if (input.type === 'email' && !input.checkValidity()) { input.focus(); alertInline('Ingresá un email válido.'); return false; }
        }
        if (step === 0 && factura === 'E' && field('facturacion_pais').value.trim().toLowerCase() === 'argentina') { alertInline('Factura E requiere un país distinto de Argentina.'); return false; }
        return true;
    }

    function alertInline(message) {
        if (window.PatitasUI?.toast) window.PatitasUI.toast(message, 'warning');
    }

    function saveDraft() {
        clearTimeout(draftTimer);
        draftTimer = setTimeout(() => {
            const data = $form.serializeArray();
            data.push({ name: 'action', value: 'save_draft' });
            $.post(form.action || location.pathname, data);
        }, 600);
    }

    $('#checkout-next').on('click', () => { if (validStep()) { showStep(step + 1); saveDraft(); } });
    $('#checkout-back').on('click', () => showStep(step - 1));
    $form.on('change input', 'input, select, textarea', function (event) {
        conditionals(event.type === 'change' && this.name === 'medio_pago');
        if (this.name !== 'comprobante') saveDraft();
    });
    $form.on('submit', function (event) {
        clearTimeout(draftTimer);
        renderSummary();
        if (!cart.getCart().length || !field('confirmar-datos').checked) { event.preventDefault(); alertInline('Revisá el carrito y confirmá los datos.'); return; }
        $('#checkout-submit').prop('disabled', true).text('Confirmando…');
    });
    $('.copy-button').on('click', async function () {
        try { await navigator.clipboard.writeText(this.dataset.copy); $('#copy-feedback').text('Copiado al portapapeles.').addClass('text-success'); }
        catch (_) { $('#copy-feedback').text('No se pudo copiar automáticamente.').addClass('text-danger'); }
    });
    conditionals();
    renderSummary();
    if ($form.find('.text-danger').length) {
        const invalid = $form.find('.text-danger').first().closest('.checkout-step-panel');
        if (invalid.length) showStep(Number(invalid.data('step')));
    } else showStep(0);
})(jQuery);
