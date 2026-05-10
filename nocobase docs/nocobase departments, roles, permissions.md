1. # Departments

   ## Department Management

   ![](<https://static-docs.nocobase.com/a6eb94a5cc85a6c7b310f33173a5259d.png>)

   ### Create a New Department

   ![](<https://static-docs.nocobase.com/4857910991ae374b63251cee99511e93.png>)

   ![](<https://static-docs.nocobase.com/0cd13d99dcd21ced0bb1683557f0b76b.png>)

   ### Create a Sub-Department

   ![](<https://static-docs.nocobase.com/0be8c7db8d12c23f6fe137e7ce23688a.png>)

   ![](<https://static-docs.nocobase.com/2db2fc2037ed383edd60117a46fc9dd0.png>)

   ### Edit Department

   ![](<https://static-docs.nocobase.com/a147319577e5cc36b5862c1e511f6722.png>)

   ![](<https://static-docs.nocobase.com/f206f866753cf30ac78aadf4f76bad32.png>)

   ### Change Superior Department

   Modify the superior department field in the department editing form. The current department and its sub-departments are not selectable.

   ![](<https://static-docs.nocobase.com/9d80ddf42f32c77186566ed8ada70128.png>)

   ## Department Member Management

   ### View Department Member List

   ![](<https://static-docs.nocobase.com/2aaf4d9bf55da105b5fca4e9f7e23ca7.png>)

   ### Add Members to the Department

   A user can join multiple departments at the same time. The first department they join is the default main department. A user only has one main department.

   ![](<https://static-docs.nocobase.com/60afd282f33b555e6fe0662b9da544cc.png>)

   Users who are already department members will not appear in the user selection list.

   ![](<https://static-docs.nocobase.com/6bcd93173c169973f970de35d2657993.png>)

   ### Set Department Head

   In the department editing form, click the head field to select department members to become heads. Multiple selections are supported. Members who are already department heads will not appear in the member selection list.

   ![](<https://static-docs.nocobase.com/92970546cbd0aeb5a8b6a36da87583bd.png>)

   ### Configure Departments for Users

   In addition to adding members to the department, you can also configure departments for users from the user's perspective.

   ![](<https://static-docs.nocobase.com/ca82a802012572e225570e8be93a4094.png>)

   Departments that have already been joined are not selectable.

   ![](<https://static-docs.nocobase.com/70e16d17ee9c4b5d43f8a5e1c633b177.png>)

   ### Change Main Department

   ![](<https://static-docs.nocobase.com/da92dd1e10268adcd35445e9f1dac771.png>)

   ## Search for Users and Departments

   Search for users by nickname, username, phone, email, and search for departments by department name.

   ![](<https://static-docs.nocobase.com/2d71346a5400205b22436b4db331a9b8.png>)

   # Department Role Management

   By associating one or more roles with a department, members of the current department can have these roles.

   There are two ways to associate roles with a department.

   The first is to select a role in the role field of the department editing form.

   ![](<https://static-docs.nocobase.com/70f77bb89aa1fb415c152a51a51cc23b.png>)

   The second is to add departments to the corresponding role in role management.

   ![](<https://static-docs.nocobase.com/f2a7bec937cf2f179ce868a92b98416d.png>)

   Departments that already have this role are not selectable.

   ![](<https://static-docs.nocobase.com/be10299893581e1f97a4e01ddd5c7e59.png>)

   # Roles

   ## Management Center

   ### Role Management

   ![](<https://static-docs.nocobase.com/da7083c67d794e23dc6eb0f85b1de86c.png>)

   The application comes with two predefined roles: "Admin" and "Member," each with distinct default permission settings tailored to their functionalities.

   ### Adding, Deleting, and Modifying Roles

   The role identifier, a unique system identifier, allows customization of default roles, but the system's predefined roles cannot be deleted.

   ![](<https://static-docs.nocobase.com/35f323b346db4f9f12f9bee4dea63302.png>)

   ### Setting the Default Role

   The default role is the one automatically assigned to new users if no specific role is provided during their creation.

   ![](<https://static-docs.nocobase.com/f41bba7ff55ca28715c486dc45bc1708.png>)

   ## Personal Center

   ### Role Switching

   Users can be assigned multiple roles and switch between them in the personal center.

   ![](<https://static-docs.nocobase.com/e331d11ec1ca3b8b7e0472105b167819.png>)

   The default role when logging in is determined by the most recently switched role (this value updates with each switch) or, if not applicable, the first role (system default role).

   # Configuring Permissions

   ## General Permission Settings

   ![](<https://static-docs.nocobase.com/119a9650259f9be71210121d0d3a435d.png>)

   ### Configuration Permissions

   1. **Allows to configure interface**: This permission governs whether a user can configure the interface. Activating it adds a UI configuration button. The "admin" role has this permission enabled by default.

   2. **Allows to install, activate, disable plugins**: This permission dictates whether a user can enable or disable plugins. When active, the user gains access to the plugin manager interface. The "admin" role has this permission enabled by default.

   3. **Allows to configure plugins**: This permission lets the user configure plugin parameters or manage plugin backend data. The "admin" role has this permission enabled by default.

   4. **Allows to clear cache, reboot application**: This permission is tied to system maintenance tasks like clearing the cache and restarting the application. Once activated, related operation buttons appear in the personal center. This permission is disabled by default.

   5. **New menu items are allowed to be accessed by default**: Newly created menus are accessible by default, and this setting is enabled by default.

   ### Global Action Permissions

   Global action permissions apply universally to all collections and are categorized by operation type. These permissions can be configured based on data scope: all data or the user's own data. The former allows operations on the entire collection, while the latter restricts operations to data relevant to the user.

   ## Collection Action Permissions

   ![](<https://static-docs.nocobase.com/6a6e0281391cecdea5b5218e6173c5d7.png>)

   ![](<https://static-docs.nocobase.com/9814140434ff9e1bf028a6c282a5a165.png>)

   Collection action permissions allow fine-tuning of global action permissions by configuring access to resources within each collection. These permissions are divided into two aspects:

   1. **Action permissions**: These include adding, viewing, editing, deleting, exporting, and importing actions. Permissions are set based on data scope:

   * **All records**: Grants the user the ability to perform actions on all records within the collection.

   * **Own records**: Restricts the user to perform actions only on records they have created.

   2. **Field Permissions**: Field permissions enable you to set specific permissions for each field during different operations. For instance, certain fields can be configured to be view-only, without editing privileges.

   ## Menu Access Permissions

   Menu access permissions control access based on menu items.

   ![](<https://static-docs.nocobase.com/28eddfc843d27641162d9129e3b6e33f.png>)

   ## Plugin Configuration Permissions

   Plugin configuration permissions control the ability to configure specific plugin parameters. When enabled, the corresponding plugin management interface appears in the admin center.

   ![](<https://static-docs.nocobase.com/5a742ae20a9de93dc2722468b9fd7475.png>)

   # Application in UI

   ## Data Block Permissions

   Visibility of data blocks in a collection is controlled by view action permissions, with individual configurations taking precedence over global settings.

   For example, under global permissions, the "admin" role has full access, but the Orders collection may have individual permissions configured, making it invisible.

   Global permission configuration:

   ![](<https://static-docs.nocobase.com/3d026311739c7cf5fdcd03f710d09bc4.png>)

   Orders collection individual permission configuration:

   ![](<https://static-docs.nocobase.com/a88caba1cad47001c1610bf402a4a2c1.png>)

   In the UI, all blocks in the Orders collection are not displayed.

   Complete configuration process:

   ![](<https://static-docs.nocobase.com/b283c004ffe0b746fddbffcf4f27b1df.gif>)

   ## Field Permissions

   **View**: Determines whether specific fields are visible at the field level, allowing control over which fields are visible to certain roles within the Orders collection.

   ![](<https://static-docs.nocobase.com/30dea84d984d95039e6f7b180955a6cf.png>)

   In the UI, only fields with configured permissions are visible within the Orders collection block. System fields (Id, CreatedAt, LastUpdatedAt) retain view permissions even without specific configuration.

   ![](<https://static-docs.nocobase.com/40cc49b517efe701147fd2e799e79dcc.png>)

   * **Edit**: Controls whether fields can be edited and saved (updated).

   Configure edit permissions for Orders collection fields (quantity and associated items have edit permissions):

   ![](<https://static-docs.nocobase.com/6531ca4122f0887547b5719e2146ba93.png>)

   In the UI, only fields with edit permissions are shown in the edit action form block within the Orders collection.

   ![](<https://static-docs.nocobase.com/12982450c311ec1bf87eb9dc5fb04650.png>)

   Complete configuration process:

   ![](<https://static-docs.nocobase.com/1dbe559a9579c2e052e194e50edc74a7.gif>)

   * **Add**: Determines whether fields can be added (created).

   Configure add permissions for Orders collection fields (order number, quantity, items, and shipment have add permissions):

   ![](<https://static-docs.nocobase.com/3ab1bbe41e61915e920fd257f2e0da7e.png>)

   In the UI, only fields with add permissions are displayed within the add action form block of the Orders collection.

   ![](<https://static-docs.nocobase.com/8d0c07893b63771c428974f9e126bf35.png>)

   * **Export**: Controls whether fields can be exported.

   * **Import**: Controls whether fields support import.

   ## Action Permissions

   Individually configured permissions take the highest priority. If specific permissions are configured, they override global settings; otherwise, the global settings are applied.

   * **Add**: Controls whether the add action button is visible within a block.

   Configure individual action permissions for the Orders collection to allow adding:

   ![](<https://static-docs.nocobase.com/2e3123b5dbc72ae78942481360626629.png>)

   When the add action is permitted, the add button appears within the action area of the Orders collection block in the UI.

   ![](<https://static-docs.nocobase.com/f0458980d450544d94c73160d75ba96c.png>)

   * **View**: Determines whether the data block is visible.

   Global permission configuration (no view permission):

   ![](<https://static-docs.nocobase.com/6e4a1e6ea92f50bf84959dedbf1d5683.png>)

   Orders collection individual permission configuration:

   ![](<https://static-docs.nocobase.com/f2dd142a40fe19fb657071fd901b2291.png>)

   In the UI, data blocks for all other collections remain hidden, but the Orders collection block is shown.

   Complete example configuration process:

   ![](<https://static-docs.nocobase.com/b92f0edc51a27b52e85cdeb76271b936.gif>)

   * **Edit**: Controls whether the edit action button is displayed within a block.

   ![](<https://static-docs.nocobase.com/fb1c0290e2a833f1c2b415c761e54c45.gif>)

   Action permissions can be further refined by setting the data scope.

   For example, setting the Orders collection so users can only edit their own data:

   ![](<https://static-docs.nocobase.com/b082308f62a3a9084cab78a370c14a9f.gif>)

   * **Delete**: Controls whether the delete action button is visible within a block.

   ![](<https://static-docs.nocobase.com/021c9e79bcc1ad221b606a9555ff5644.gif>)

   * **Export**: Controls whether the export action button is visible within a block.

   * **Import**: Controls whether the import action button is visible within a block.

   ## Association Permissions

   ### As a Field

   * The permissions of an association field are controlled by the field permissions of the source collection. This controls whether the entire association field component is displayed.

   For example, in the Orders collection, the association field "Customer" only has view, import, and export permissions.

   ![](<https://static-docs.nocobase.com/d0dc797aae73feeabc436af285dd4f59.png>)

   In the UI, this means the "Customer" association field will not be displayed in the add and edit action blocks of the Orders collection.

   Complete example configuration process:

   ![](<https://static-docs.nocobase.com/372f8a4f414feea097c23b2ba326c0ef.gif>)

   * The permissions for fields within the association field component (such as a sub-table or sub-form) are determined by the permissions of the target collection.

   When the association field component is a sub-form:

   As shown below, the "Customer" association field in the Orders collection has all permissions, while the Customers collection itself is set to read-only.

   Individual permission configuration for the Orders collection, where the "Customer" association field has all field permissions:

   ![](<https://static-docs.nocobase.com/3a3ab9722f14a7b3a35361219d67fa40.png>)

   Individual permission configuration for the Customers collection, where fields have view-only permissions:

   ![](<https://static-docs.nocobase.com/46704d179b931006a9a22852e6c5089e.png>)

   In the UI, the "Customer" association field is visible in the Orders collection block. However, when switched to a sub-form, the fields within the sub-form are visible in the details view but are not displayed in the add and edit actions.

   Complete example configuration process:

   ![](<https://static-docs.nocobase.com/932dbf6ac46e36ee357ff3e8b9ea1423.gif>)

   To further control permissions for fields within the sub-form, you can grant permissions to individual fields.

   As shown, the Customers collection is configured with individual field permissions (Customer Name is not visible and not editable).

   ![](<https://static-docs.nocobase.com/e7b875521cbc4e28640f027f36d0413c.png>)

   Complete example configuration process:

   ![](<https://static-docs.nocobase.com/7a07e68c2fe2a13f0c2cef19be489264.gif>)

   When the association field component is a sub-table, the situation is consistent with that of a sub-form:

   As shown, the "Shipment" association field in the Orders collection has all permissions, while the Shipments collection is set to read-only.

   In the UI, this association field is visible. However, when switched to a sub-table, the fields within the sub-table are visible in the view action but not in the add and edit actions.

   ![](<https://static-docs.nocobase.com/fd4b7d81cdd765db789d9c85cf9dc324.gif>)

   To further control permissions for fields within the sub-table, you can grant permissions to individual fields:

   ![](<https://static-docs.nocobase.com/51d70a624cb2b0366e421bcdc8abb7fd.gif>)

   ### As a Block

   * The visibility of an association block is controlled by the permissions of the target collection of the corresponding association field, and is independent of the association field's permissions.

   For example, whether the "Customer" association block is displayed is controlled by the permissions of the Customers collection.

   ![](<https://static-docs.nocobase.com/633ebb301767430b740ecfce11df47b3.gif>)

   * The fields within an association block are controlled by the field permissions in the target collection.

   As shown, you can set view permissions for individual fields in the Customers collection.

   ![](<https://static-docs.nocobase.com/35af9426c20911323b17f67f81bac8fc.gif>)

   # Role Union

   Role Union is a permission management mode. According to system settings, system developers can choose to use `Independent roles`, `Allow roles union`, or `Roles union only`, to meet different permission requirements.

   ![20250312184651](<https://static-docs.nocobase.com/20250312184651.png>)

   ## Independent roles

   By default, the system uses independent roles. Users must switch between the roles they possess individually.

   ![20250312184729](<https://static-docs.nocobase.com/20250312184729.png>)

   ![20250312184826](<https://static-docs.nocobase.com/20250312184826.png>)

   ## Allow roles union

   System developers can enable `Allow roles union`, allowing users to simultaneously have permissions of all assigned roles while still permitting users to switch roles individually.

   ![20250312185006](<https://static-docs.nocobase.com/20250312185006.png>)

   ## Roles union only

   Users are enforced to only use Role Union and cannot switch roles individually.

   ![20250312185105](<https://static-docs.nocobase.com/20250312185105.png>)

   ## Rules for Role Union

   Role union grants the maximum permissions across all roles. Below are the explanations for resolving permission conflicts when roles have different settings on the same permission.

   ### Operation Permission Merge

   Example:\

   Role1 is configured to `Allows to configure interface` and Role2 is configured to `Allows to install, activate, disable plugins`

   ![20250312190133](<https://static-docs.nocobase.com/20250312190133.png>)

   ![20250312190352](<https://static-docs.nocobase.com/20250312190352.png>)

   When logging in with the **Full Permissions** role, the user will have both permissions simultaneously.

   ![20250312190621](<https://static-docs.nocobase.com/20250312190621.png>)

   ### Data Scope Merge

   #### Data Rows

   Scenario 1: Multiple roles setting conditions on the same field

   Role A filter: Age < 30

   | UserID | Name | Age |

   | ------ | ---- | --- |

   | 1 | Jack | 23 |

   | 2 | Lily | 29 |

   Role B filter: Age > 25

   | UserID | Name | Age |

   | ------ | ---- | --- |

   | 2 | Lily | 29 |

   | 3 | Sam | 32 |

   **After merging:**

   | UserID | Name | Age |

   | ------ | ---- | --- |

   | 1 | Jack | 23 |

   | 2 | Lily | 29 |

   | 3 | Sam | 32 |

   Scenario 2: Different roles setting conditions on different fields

   Role A filter: Age < 30

   | UserID | Name | Age |

   | ------ | ---- | --- |

   | 1 | Jack | 23 |

   | 2 | Lily | 29 |

   Role B filter: Name contains "Ja"

   | UserID | Name | Age |

   | ------ | ------ | --- |

   | 1 | Jack | 23 |

   | 3 | Jasmin | 27 |

   **After merging:**

   | UserID | Name | Age |

   | ------ | ------ | --- |

   | 1 | Jack | 23 |

   | 2 | Lily | 29 |

   | 3 | Jasmin | 27 |

   #### Data Columns

   Role A visible columns: Name, Age

   | UserID | Name | Age |

   | ------ | ---- | --- |

   | 1 | Jack | 23 |

   | 2 | Lily | 29 |

   Role B visible columns: Name, Sex

   | UserID | Name | Sex |

   | ------ | ---- | ----- |

   | 1 | Jack | Man |

   | 2 | Lily | Woman |

   **After merging:**

   | UserID | Name | Age | Sex |

   | ------ | ---- | --- | ----- |

   | 1 | Jack | 23 | Man |

   | 2 | Lily | 29 | Woman |

   #### Mixed Rows and Columns

   Role A filter: Age < 30, columns Name, Age

   | UserID | Name | Age |

   | ------ | ---- | --- |

   | 1 | Jack | 23 |

   | 2 | Lily | 29 |

   Role B filter: Name contains "Ja", columns Name, Sex

   | UserID | Name | Sex |

   | ------ | ----- | ----- |

   | 3 | Jade | Woman |

   | 4 | James | Man |

   **After merging:**

   | UserID | Name | Age | Sex |

   | ------ | ----- | ------------------------------------------------ | --------------------------------------------------- |

   | 1 | Jack | 23 | &lt;span style="background-color:#FFDDDD"&gt;Man&lt;/span&gt; |

   | 2 | Lily | 29 | &lt;span style="background-color:#FFDDDD"&gt;Woman&lt;/span&gt; |

   | 3 | Jade | &lt;span style="background-color:#FFDDDD"&gt;27&lt;/span&gt; | Woman |

   | 4 | James | &lt;span style="background-color:#FFDDDD"&gt;31&lt;/span&gt; | Man |

   **Note: Cells with red background indicate data invisible in individual roles but visible in the merged role.**

   #### Summary

   Role merging data-scope rules:

   1. Between rows, if any condition is satisfied, the row has permissions.

   2. Between columns, fields are combined.

   3. When rows and columns are both configured, rows and columns are merged separately, not by row-column combinations.