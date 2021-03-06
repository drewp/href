$("#filterTag").focus();

var model = {
    filterTags: ko.observableArray(tagsFromWindowLocation())
};

function componentsAfterRoot() {
    var p = window.location.href;
    return comps = p.substr(toRoot.length + 1).split("/");
}

function tagsFromWindowLocation() {
    var comps = componentsAfterRoot();
    comps.shift();
    if (!comps.length) {
        return [];
    }
    var tags = comps[0].replace("%20", "+").split("+");
    return tags.filter(function(t) { return t != ""; });
}

function toggleTag(tag) {
    var selected = model.filterTags();

    if (selected.indexOf(tag) == -1) {
        selected.push(tag);
    } else {
        selected.splice(selected.indexOf(tag), 1);
    }
    model.filterTags(selected);
}

function initSpecialLinkBehavior() {
    // clicking tag links doesn't go to them (they're not
    // user-specific); it toggles their presence in our page's current
    // filter list   
    $(document).on("click", "a.tag", function (ev) {
        var tag = $(this).text();
        toggleTag(tag);
        ev.stopPropagation()
        ev.preventDefault()
        return false;
    });
}
            
var linklist = null;
// unsure how to use toRoot- can it change?
$.getJSON(toRoot + "/templates", function (result) {
    linklist = result.linklist;
});

function pathFromUserAndTags(tags) {
    var comps = componentsAfterRoot();
    var newPath = comps[0];
    if (tags.length) {
        newPath += '/' + tags.join('+');
    }
    return newPath;
}

function initUrlSync(model) {
    // tag changes push url history; and url edits freshen the page

    ko.computed(function () {
        var tags = model.filterTags();
        var newPath = pathFromUserAndTags(tags);
        changePage(newPath);
    });

    function changePage(newPath) {
        if (componentsAfterRoot().join('/') != newPath) {
            window.history.pushState({}, "", toRoot + '/' + newPath);

            function updateLinklist(fullPath) {
                var t0 = +new Date();
                if (linklist === null) {
                    console.log("too soon- templates aren't loaded");
                    return;
                }
                $(".linklist").text("Loading...");
                $.getJSON(toRoot + '/' + fullPath + ".json", function (result) {
                    var t1 = +new Date();
                    var rendered = Mustache.render(linklist, result)
                    var t2 = +new Date();
                    $(".linklist").html(rendered);
                    var t3 = +new Date();
                    $(".stats").text(JSON.stringify({
                        "getMs": t1 - t0,
                        "mustacheRenderMs": t2 - t1,
                        "setHtmlMs": t3 - t2
                    }));
                });
            }
            updateLinklist(newPath);
        }    
    }   
}

function initFilterTag(elem, model) {
    // sync the entry box and the model
    
    elem.change(function () {
        var tags = $(this).val().split(",");
        model.filterTags(tags.filter(function(t) { return t != ""; }));
        return false;
    });

    var filterCompleteWords = "";
    elem.select2({
        allowClear: true,
        multiple: true,
        tokenSeparators: [' ', ','],
        query: function (opts) {
            $.ajax({
                url: toRoot + "/tags",
                data: {user: user, have: opts.element.val() + "," + opts.term},
                success: function (data) {
                    // I don't want to do this, but select2 gets too slow
                    var maxRowsInAutocomplete = 300;
                    if (data.tags.length > maxRowsInAutocomplete) { 
                        data.tags = data.tags.slice(0, maxRowsInAutocomplete);
                    }
                    opts.callback({results: data.tags});
                }
            });
        },
        change: function (ev) {
            console.log("ch", ev.val);
        },
        initSelection: function (element, callback) {
            var data = [];
            $(element.val().split(",")).each(function () {
                if (this != "") {
                    data.push({id: this, text: this});
                }
            });
            callback(data);
        }
    });
    ko.computed(function () {
        elem.select2("val", model.filterTags());
    });
}

initFilterTag($("#filterTag"), model);
initSpecialLinkBehavior();
initUrlSync(model);

ko.applyBindings(model);
