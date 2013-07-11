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

(function (inputElem, model) {
    inputElem.select2({
        tokenSeparators: [",", " "],
        ajax: {
            url: "/foaf/findPerson",
            data: function (term, page) {
                return {q: term};
            },
            results: function (data, page) {
                var ret = {
                    results: data.people.map(
                        function (row) {
                            return {id: row.uri,
                                    text: row.label + " ("+row.uri+")"};
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
    inputElem.on('change', function (e) {
        console.log("onchange", inputElem.select2('val'));
        setModelFromShares(inputElem.select2('val'));
    });

    var enableModel = true;

    var setSharesFromModel = ko.computed(
        function () {
            var uris = ko.utils.arrayGetDistinctValues(model.linkRecord.shareWith());
            if (!enableModel) {
                return;
            }
            console.log("from model", uris)

            async.map(uris,
                      function (uri, cb) {
                          $.ajax({
                              url: uri.replace(/^http:/, "https:"),
                              dataType: "text",
                              success: function (page) {
                                  pp = page
                                  d = $(page).rdfa().databank;
                                  console.log("from", uri, "extracted", d.size(), "triples");
                                  "trying to get the rdfa out of this page to attempt prettier label/icon for the listed person"
                                  console.log(JSON.stringify(d.dump()));
                              }
                          });
                          cb(null, {id: uri, text: "("+uri+")"});
                      },
                      function (err, selections) {
                          inputElem.select2("data", selections);
                      });
        });

    function setModelFromShares(n) {
        console.log("from val", inputElem.select2("val"), "new", n)
        enableModel = false;
        model.linkRecord.shareWith(inputElem.select2("val"));
        enableModel = true;
    }
    
    //  setSharesFromModel();
})($("#shareWith"), model);


