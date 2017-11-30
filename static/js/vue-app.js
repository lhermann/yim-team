var config = {
    volunteerAreas: {
        Kongressleitung: {},
        Küche: { kitchen: "Küche" },
        Logistik: {
            maintenance: "Sauberkeit",
            setup: "Aufbau",
            teardown: "Abbau"
        },
        Musik: {},
        Öffentlichkeitsarbeit: {},
        Outreach: {},
        Programm: { ushers: "Saalordnung" },
        Registrierung: { registration: "Registrierung" },
        Sicherheit: { security: "Security", surroundings: "Außenbereich" },
        Technik: { wsaudio: "Workshop Audio" },
        "WS & Referenten": {},
        "YiM-Leben": {}
    }
};

/* Set up Axios
 **********************/
axios.defaults.headers = { "X-Requested-With": "XMLHttpRequest" };
axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/* Helpers Component
 **********************/

Vue.component("helfer-table", {
    template: "#table-template",
    data: function() {
        return {
            // Default values
            email: "",
            label: this.labelPreset,
            foodPrivilege: true,
            above35: true,
            axiosBusy: false,
            axiosError: "",
            itemOldState: {},
            tShirtSizes: [
                "-",
                "S Men",
                "M Men",
                "L Men",
                "XL Men",
                "XXL Men",
                "XS Lady Fit",
                "S Lady Fit",
                "M Lady Fit",
                "L Lady Fit",
                "XL Lady Fit",
                "XXL Lady Fit"
            ],
            tShirtSize: "-"
        };
    },
    computed: {
        // a computed getter
        filteredItems: function() {
            return this.items.filter(function(item) {
                return item.freeAdmission == this;
            }, this.freeAdmission == "true");
        },
        prefix: function() {
            return this.freeAdmission == "true" ? "frei" : "zahlt";
        }
    },
    props: ["items", "area", "label-preset", "free-admission"],
    methods: {
        addItem: function() {
            console.log("add");
            var component = this;
            var item = {
                email: _.trim(component.email),
                label: _.trim(component.label),
                area: component.area,
                freeAdmission: component.freeAdmission === "true",
                foodPrivilege: component.foodPrivilege,
                above35: component.above35,
                tShirtSize: component.tShirtSize
            };
            component.axiosError = "";
            component.axiosBusy = true;
            axios
                .post("/helpers/", camelToSnake(item))
                .then(function(response) {
                    component.axiosBusy = false;
                    item.editing = false;
                    item.regId = false;
                    item.url = response.data.url;
                    component.items.push(item);
                    component.email = ""; // clear field
                })
                .catch(function(error) {
                    component.axiosBusy = false;
                    component.axiosError = Object.values(
                        error.response.data
                    )[0][0];
                });
        },
        removeItem: function(index) {
            var item = this.items[index];
            var component = this;
            if (confirm(item.email + " löschen?")) {
                this.axiosError = "";
                this.axiosBusy = true;
                axios
                    .delete(item.url)
                    .then(function(response) {
                        component.axiosBusy = false;
                        component.items.splice(index, 1);
                    })
                    .catch(function(error) {
                        component.axiosBusy = false;
                        if (error.response) {
                            component.axiosError = error.response.data.pop();
                        }
                    });
            }
        },
        editItem: function(item) {
            Object.assign(this.itemOldState, item);
            item.editing = true;
        },
        cancelEdit: function(item) {
            item.editing = false;
        },
        doneEdit: function(item) {
            var component = this;
            this.axiosError = "";
            this.axiosBusy = true;
            axios
                .patch(item.url, camelToSnake(item))
                .then(function(response) {
                    component.axiosBusy = false;
                    item.editing = false;
                })
                .catch(function(error) {
                    component.axiosBusy = false;
                    if (error.response) {
                        component.axiosError = Object.values(
                            error.response.data
                        )[0][0];
                        Object.assign(item, component.itemOldState);
                    }
                });
        }
    }
});

/* Volunteers Component
 **********************/

Vue.component("volunteer-table", {
    template: "#volunteer-template",
    data: function() {
        return {
            list: []
        };
    },
    computed: {
        listSorted: function() {
            var list = this.list;
            list.sort(function(a, b) {
                return a.lastname > b.lastname
                    ? 1
                    : b.lastname > a.lastname ? -1 : 0;
            });
            return list;
        },
        emailListComma: function() {
            var list = "";
            this.list.forEach(function(v) {
                list += v.email + ", ";
            });
            return list.substr(0, list.length - 2);
        }
    },
    props: ["area", "label"],
    methods: {
        hasPayed: function(volunteer) {
            return volunteer.payment_date != null;
        }
    },
    mounted() {
        var component = this,
            request = "/registerseat/";
        switch (this.area) {
            case "setup":
            case "teardown":
                request += "10/" + this.area;
                break;
            default:
                request += "14/" + this.area;
        }
        axios
            .get(request)
            .then(function(response) {
                component.list = response.data;
            })
            .catch(function(error) {
                console.log(error);
            });
    }
});

/* Vue App
 **********************/

var app = new Vue({
    el: "#app",
    data: {
        area: "",
        volunteerAreas: {},
        items: []
    },
    mounted() {
        axios
            .get("/helpers/")
            .then(function(response) {
                var items = snakeToCamel(response.data);
                items.forEach(function(obj) {
                    obj.editing = false;
                });
                this.app.items = snakeToCamel(items);
                this.app.area = response.headers["data-user"];
                this.app.volunteerAreas = config.volunteerAreas[this.app.area];
            })
            .catch(function(error) {
                console.log(error);
            });
    }
});

/* Helper Functions
 **********************/

//Cookie:sessionid=7vbxih5nlwpgqxcwdndg5zk11n6pdy15; csrftoken=wJtZEH1wRQUzJC5k9VJbzk7Cl0vRqNflPS9bnMWb7o9bJQgPkYwvkbV9r52Cdh7m
//Cookie:sessionid=7vbxih5nlwpgqxcwdndg5zk11n6pdy15; csrftoken=wJtZEH1wRQUzJC5k9VJbzk7Cl0vRqNflPS9bnMWb7o9bJQgPkYwvkbV9r52Cdh7m

// Test
// var object = { snake_case_index: "test value", camelCaseIndex: "test value" };
// console.log(manipulateCase(object, "camel"));
// var obj = {
//     email: "abc@gmail.com",
//     label: "Some Nice Label",
//     area: "TEST",
//     freeAdmission: true,
//     foodPrivilege: true,
//     above35: true
// };
// axios.post("/helpers/", camelToSnake(obj)).then(function(response) {
//     console.log(response);
// });

function snakeToCamel(input) {
    return manipulateCase(input, "camel");
}
function camelToSnake(input) {
    return manipulateCase(input, "snake");
}
function manipulateCase(input, to) {
    if (input instanceof Array) {
        var newArr = [];
        input.forEach(function(obj, i) {
            newArr[i] = manipulateCase(obj, to);
        });
        return newArr;
    } else if (input instanceof Object) {
        var newObj = {};
        _.forIn(input, function(value, key) {
            switch (to) {
                case "camel":
                    newObj[_.camelCase(key)] = value;
                    break;
                case "snake":
                    newObj[_.snakeCase(key)] = value;
                    break;
            }
        });
        return newObj;
    }
}
