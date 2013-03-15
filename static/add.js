var model = {
    linkRecord: {
        href: ko.observable(""),
        description: ko.observable(""),
        tag: ko.observable(""),
        extended: ko.observable(""),
        private: ko.observable(false),
        shareWith: ko.observableArray([]), // foaf uris
    },
    submitLabel: ko.observable("Add"),
};

ko.computed(function() {
    if (model.linkRecord.href() == "") {
        return;
    }

    $.getJSON("addLink/proposedUri", {uri: model.linkRecord.href()}, function (data) {
        // these could arrive after the user has started typing in the fields!
        
        model.linkRecord.description(data.description);
        model.linkRecord.tag(data.tag);
        model.linkRecord.extended(data.extended);
        model.linkRecord.shareWith(data.shareWith);
        model.submitLabel(data.existed ? "Update existing" : "Add");
        
    });
    
});

ko.applyBindings(model);

$("#shareWith").select2({
    tokenSeparators: [",", " "],
    ajax: {
        url: "/foaf/findPerson",
        data: function (term, page) {
            return {q: term};
        },
        results: function (data, page) {
            var ret = {results: data.people.map(
                function (row) {
                    return {id: row.uri, text: row.label + " ("+row.uri+")"}
                }),
                       more: false,
                       context: {}
                      };
            //ret.results.push({id: "new1", text: this.context});
            return ret;
        }
    },
    tags: [],
});
$("#shareWith").on('change', function (e) { setModelFromShares(e.val); });

var setSharesFromModel = ko.computed(
    function () {
        var uris = ko.utils.arrayGetDistinctValues(model.linkRecord.shareWith());
        console.log("from model", uris)
        $("#shareWith").select2("data", uris.map(
            function (uri) {
                return {id: uri, text: "("+uri+")"};
            }));
    });

function setModelFromShares(n) {
    console.log("from val", $("#shareWith").select2("val"), "new", n)
    model.linkRecord.shareWith($("#shareWith").select2("val"));
}

setSharesFromModel();
