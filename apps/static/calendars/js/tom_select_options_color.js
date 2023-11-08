document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.select, .selectmultiple').forEach((el) => {
        let settings = {
            placeholder: 'Rechercher ou sélectionner',
            render: {
                option: function(data, escape) {
                    bg_color= "background-color: " + eventColors[data.text] + ";";
                    // Define custom styles for each option/ Customize this as needed
                    return '<div style="' + bg_color + '">' + escape(data.text) + '</div>';
                }
            }
        };
        var select = new TomSelect(el, settings);
        console.log(select)
        //select.on('initialize', handler);
    });

    document.querySelectorAll('.ts-wrapper').forEach((el) => {
        el.classList.remove('form-select');

    });
});