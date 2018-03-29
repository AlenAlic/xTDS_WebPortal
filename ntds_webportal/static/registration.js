function onStart() {
    document.getElementById('ballroom_level').onchange();
    document.getElementById('latin_level').onchange();
    document.getElementById('volunteer').onchange();
}
function dropDownGreyOut(parent_id, id) {
    var ddl = document.getElementById(id);
    var parentDiv = document.getElementById(parent_id);
    selectedValue = ddl.options[ddl.selectedIndex].value;
    if (selectedValue == "no") {
        $(parentDiv).find('*').attr('disabled', true);
    } else {
        $(parentDiv).find('*').attr('disabled', false);
        blindDateGreyOut('ballroom_p', 'ballroom_blind_date')
        blindDateGreyOut('latin_p', 'latin_blind_date')
    }
}
//function blindDateGreyOut(partner_id, check_id) {
//    var bdcb = document.getElementById(check_id);
//    var checkDiv = document.getElementById(partner_id);
//    var selectedValue = bdcb.checked;
//    if (selectedValue == true || bdcb.disabled == true) {
//        $(checkDiv).find('*').attr('disabled', true);
//    } else {
//        $(checkDiv).find('*').attr('disabled', false);
//    }
//}