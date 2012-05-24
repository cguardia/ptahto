from pyramid.security import ALL_PERMISSIONS

import ptah

View = ptah.Permission('ptah:View', 'View')
AddContent = ptah.Permission('ptahto:AddContent', 'Add content')
ModifyContent = ptah.Permission('ptahto:EditContent', 'Modify content')
DeleteContent = ptah.Permission('ptahto:DeleteContent', 'Delete content')

ptah.Everyone.allow(View)
ptah.Authenticated.allow(AddContent)
ptah.Authenticated.allow(ModifyContent)

Manager = ptah.Role('manager', 'Manager')
Manager.allow(ALL_PERMISSIONS)

ptah.Owner.allow(DeleteContent)
