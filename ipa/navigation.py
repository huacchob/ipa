"""Menu items."""

from nautobot.apps.ui import NavMenuAddButton, NavMenuGroup, NavMenuItem, NavMenuTab

items = (
    NavMenuItem(
        link="plugins:ipa:ipaexamplemodel_list",
        name="Ipa",
        permissions=["ipa.view_ipaexamplemodel"],
        buttons=(
            NavMenuAddButton(
                link="plugins:ipa:ipaexamplemodel_add",
                permissions=["ipa.add_ipaexamplemodel"],
            ),
        ),
    ),
)

menu_items = (
    NavMenuTab(
        name="Apps",
        groups=(NavMenuGroup(name="Ipa", items=tuple(items)),),
    ),
)
