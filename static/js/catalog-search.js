(function ($) {
    'use strict';

    $(function () {
        const $input = $('#navbar-catalog-search');
        if (!$input.length || !$.ui?.autocomplete) return;

        const endpoint = $input.data('search-url');
        if (!endpoint) return;

        $input.autocomplete({
            minLength: 2,
            delay: 180,
            source(request, response) {
                $.getJSON(endpoint, { term: request.term })
                    .done((data) => response(Array.isArray(data) ? data : (data.results || [])))
                    .fail(() => response([]));
            },
            focus(event) { event.preventDefault(); },
            select(event, ui) {
                event.preventDefault();
                if (ui.item.url) window.location.href = ui.item.url;
            }
        });

        const autocomplete = $input.autocomplete('instance');
        if (!autocomplete) return;

        autocomplete._renderItem = function (ul, item) {
            const esc = window.PatitasEscapeHtml || ((value) => String(value ?? ''));
            const image = item.imagen_url
                ? `<img src="${esc(item.imagen_url)}" alt="">`
                : `<i class="bi ${String(item.tipo || '').toLowerCase() === 'producto' ? 'bi-bag-heart' : 'bi-heart-pulse'}"></i>`;
            const price = item.precio ? `<span class="search-result-price">$${esc(item.precio)}</span>` : '';
            return $('<li>')
                .append(`
                    <div class="search-result-item">
                        <span class="search-result-thumb">${image}</span>
                        <span class="search-result-copy">
                            <strong>${esc(item.value || item.label)}</strong>
                            <small>${esc(item.tipo || '')}</small>
                        </span>
                        ${price}
                    </div>`)
                .appendTo(ul);
        };
    });
})(jQuery);
