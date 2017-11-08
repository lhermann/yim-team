Vue.component("helfer-table", {
    template: "#table-template",
    data: function() {
        return {
            items: []
        };
    },
    props: ["email", "label", "free-admission", "food-privelege"],
    methods: {
        addItem: function() {
            this.items.push({
                email: this.email,
                label: this.label,
                eventId: false,
                editing: false
            });
        },
        removeItem: function(index) {
            if (confirm(this.items[index].email + " löschen?")) {
                this.items.splice(index, 1);
            }
        },
        editItem: function(item) {
            console.log(item);
            item.editing = true;
        },
        cancelEdit: function(item) {
            item.editing = false;
        },
        doneEdit: function(item) {
            item.editing = false;
        }
    }
});

var app = new Vue({
    el: "#app",
    data: {
        area: "Registrierung"
    }
});
