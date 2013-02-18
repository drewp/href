
$("#filterTag").focus();

function toggleTag(tag) {
    var p = window.location.pathname;
    var comps = p.split("/");
    var selected = (comps[2] || "").split("+");
    var add = true;
    var others = [];
    for (var i=0; i < selected.length; i++) {
        if (!selected[i]) {
            continue;
        }
        if (selected[i] == tag) {
            add = false;
        } else {
            others.push(selected[i]);
        }
    }
    if (add) {
        others.push(tag);
    }
    window.location.pathname = "/" + comps[1] + "/" + others.join("+");
}

function backspaceLastTag() {
    var p = window.location.pathname;
    var comps = p.split("/");
    var selected = (comps[2] || "").split("+");
    if (selected.length == 0) {
        return;
    }
    toggleTag(selected[selected.length-1]);
}

$("a.tag").click(function () {
    var tag = $(this).text();
    toggleTag(tag);
    return false;
});

$("#filterTag").change(function () {
    var tag = $(this).val();
    toggleTag(tag);
    return false;
});

$("#filterTag").keydown(function (ev) {
    if ($(this).val() == "" && ev.which == 8) {
        backspaceLastTag();
    }
});
