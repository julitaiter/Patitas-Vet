(function ($) {
    "use strict";

    $(function () {
        const $input = $("#navbar-catalog-search");
        if (!$input.length || !$.ui || !$.ui.autocomplete) return;

        $input.autocomplete({
            source: $input.data("search-url"),
            minLength: 2,
            delay: 250,
            select: function (event, ui) {
                event.preventDefault();
                window.location.href = ui.item.url;
            }
        }).autocomplete("instance")._renderItem = function (ul, item) {
            const $content = $("<div>", { class: "catalog-search-result" });
            if (item.imagen_url) {
                $("<img>", {
                    src: item.imagen_url,
                    alt: "",
                    class: "catalog-search-thumbnail rounded"
                }).appendTo($content);
            } else {
                $("<span>", { class: "catalog-search-thumbnail rounded bg-light" })
                    .append($("<i>", { class: "bi bi-image" }))
                    .appendTo($content);
            }
            const $text = $("<span>");
            $("<strong>").text(item.value).appendTo($text);
            $("<small>", { class: "d-block text-muted" })
                .text(`${item.tipo} · $ ${item.precio}`)
                .appendTo($text);
            $content.append($text);
            return $("<li>").append($content).appendTo(ul);
        };
    });
})(jQuery);
