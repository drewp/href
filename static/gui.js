
$("#filterTag").focus();

var model = {
    filterTags: ko.observableArray(currentFilter())
};

function currentFilter() {
    var p = window.location.pathname;
    var comps = p.split("/");
    if (toRoot == ".") {
        return [];
    } else {
        return (comps[comps.length-1] || "").split("+");
    }
}

function toggleTag(tag) {
    var selected = currentFilter();

    if (selected.indexOf(tag) == -1) {
        selected.push(tag);
    } else {
        selected.splice(selected.indexOf(tag), 1);
    }
    setPageTags(selected);
}

function setPageTags(tags) {
    
    var newPath = window.location.pathname;
    if (toRoot == ".") {
        newPath += "/";
    } else {
        newPath = newPath.replace(
                /(.*\/)[^\/]*$/, "$1")
    }
    console.log("user root", newPath);
    if (tags.length) {
        newPath += tags.join("+")
    } else {
        newPath = newPath.substr(0, newPath.length - 1);
    }
    console.log("done", newPath);
    
    window.location.pathname = newPath;
}

function backspaceLastTag() {
    var p = window.location.pathname;
    var comps = p.split("/");
    var selected = (comps[comps.length-1] || "").split("+");
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
    var tags = $(this).val();
    setPageTags(tags);
    return false;
});

$("#filterTag").keydown(function (ev) {
    if ($(this).val() == "" && ev.which == 8) {
        backspaceLastTag();
    }
});

$("#filterTag").chosen({

    });

ko.applyBindings(model);
$("#filterTag").trigger("liszt:updated");

