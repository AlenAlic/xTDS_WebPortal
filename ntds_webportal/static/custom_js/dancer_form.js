function dancingLevelGreyOut(level, role, partner, bd) {
    var div_level = document.getElementById(level);
    var div_role = document.getElementById(role);
    var div_partner = document.getElementById(partner);
    var div_bd = document.getElementById(bd);

    val_level = div_level.options[div_level.selectedIndex].value;
    if (val_level == "{{data.NO}}") {
        div_role.setAttribute('disabled', true);
        div_partner.setAttribute('disabled', true);
        <!--div_bd.setAttribute('disabled', true);-->
    } else {
        div_role.removeAttribute('disabled');
        div_partner.removeAttribute('disabled');
        <!--div_bd.removeAttribute('disabled');-->
    }
    if ({{data.BLIND_DATE_LEVELS|safe}}.includes(val_level) || val_level == "{{data.NO}}") {
        div_partner.setAttribute('disabled', true);
    } else {
        div_partner.removeAttribute('disabled');
    }
}
function dancingBDGreyOut(bd, partner) {
    var div_partner = document.getElementById(partner);
    var div_bd = document.getElementById(bd);

    if (div_bd.checked == true) {
        div_partner.setAttribute('disabled', true);
    } else {
        div_partner.removeAttribute('disabled');
    }
}