function set_preview_href() {
    url = $(this).closest('.url_box').find(".url_box_input")[0].value; // fetches value from input
    if (url.substring(0, 7) != "http://" && url.substring(0, 8) != "https://") {
        url = "http://" + url;
    }
    this.href = url;
}

$(".preview-btn").click(set_preview_href);
