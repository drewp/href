var model = {
    href: ko.observable("starter"),
};

ko.computed(function() {
    if (model.href() == "") {
        return;
    }

    $.getJSON("proposal", {uri: model.href()}, function (data) {

    });
    
});

ko.applyBindings(model);
