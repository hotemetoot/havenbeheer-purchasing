# Configuring Permissions

## General Permission Settings

![](https://static-docs.nocobase.com/119a9650259f9be71210121d0d3a435d.png)

### Configuration Permissions

1. **Allows to configure interface**: This permission governs whether a user can configure the interface. Activating it adds a UI configuration button. The "admin" role has this permission enabled by default.
2. **Allows to install, activate, disable plugins**: This permission dictates whether a user can enable or disable plugins. When active, the user gains access to the plugin manager interface. The "admin" role has this permission enabled by default.
3. **Allows to configure plugins**: This permission lets the user configure plugin parameters or manage plugin backend data. The "admin" role has this permission enabled by default.
4. **Allows to clear cache, reboot application**: This permission is tied to system maintenance tasks like clearing the cache and restarting the application. Once activated, related operation buttons appear in the personal center. This permission is disabled by default.
5. **New menu items are allowed to be accessed by default**: Newly created menus are accessible by default, and this setting is enabled by default.

### Global Action Permissions

Global action permissions apply universally to all collections and are categorized by operation type. These permissions can be configured based on data scope: all data or the user's own data. The former allows operations on the entire collection, while the latter restricts operations to data relevant to the user.

## Collection Action Permissions

![](https://static-docs.nocobase.com/6a6e0281391cecdea5b5218e6173c5d7.png)

![](https://static-docs.nocobase.com/9814140434ff9e1bf028a6c282a5a165.png)

Collection action permissions allow fine-tuning of global action permissions by configuring access to resources within each collection. These permissions are divided into two aspects:

1. **Action permissions**: These include adding, viewing, editing, deleting, exporting, and importing actions. Permissions are set based on data scope:
   * **All records**: Grants the user the ability to perform actions on all records within the collection.
   * **Own records**: Restricts the user to perform actions only on records they have created.

2. **Field Permissions**: Field permissions enable you to set specific permissions for each field during different operations. For instance, certain fields can be configured to be view-only, without editing privileges.

## Menu Access Permissions

Menu access permissions control access based on menu items.

![](https://static-docs.nocobase.com/28eddfc843d27641162d9129e3b6e33f.png)

## Plugin Configuration Permissions

Plugin configuration permissions control the ability to configure specific plugin parameters. When enabled, the corresponding plugin management interface appears in the admin center.

![](https://static-docs.nocobase.com/5a742ae20a9de93dc2722468b9fd7475.png)


# Roles & Permissions

> Different roles see different menus and can operate on different data when they log in to the CRM. This chapter answers one question: **"What can I see, and what can I do?"**

## What Is My Role?

Roles come from two sources:

1. **Personal role** — A role directly assigned to you by an Admin; it follows you wherever you go
   ![08-roles-2026-04-07-01-45-14](https://static-docs.nocobase.com/08-roles-2026-04-07-01-45-14.png)

2. **Department role** — A role bound to your department; you inherit it automatically when you join the department

![08-roles-2026-04-07-01-46-57](https://static-docs.nocobase.com/08-roles-2026-04-07-01-46-57.png)

Both sources stack. For example, if you personally have the "Sales Rep" role and are also added to the Marketing department, you hold the permissions of both the Sales and Marketing roles.

![en\_08-roles](https://yifan2-500g.oss-cn-hangzhou.aliyuncs.com/crm-guide-mermaid/en_08-roles.png)

> \* **Sales Manager** and **Executive** are not bound to any department; they are assigned directly to individuals by the Admin.

***

## Pages Visible to Each Role

After logging in, the menu bar only shows pages you have permission to access:

![en\_08-roles\_1](https://yifan2-500g.oss-cn-hangzhou.aliyuncs.com/crm-guide-mermaid/en_08-roles_1.png)

> ¹ Sales Reps only see the SalesRep personal dashboard; they cannot see the SalesManager or Executive views.

![08-roles-2026-04-07-01-47-48](https://static-docs.nocobase.com/08-roles-2026-04-07-01-47-48.png)

***

## What Data Can I Operate On?

### Core Logic of Data Permissions

![en\_08-roles\_2](https://yifan2-500g.oss-cn-hangzhou.aliyuncs.com/crm-guide-mermaid/en_08-roles_2.png)

### Sales Rep Data Permissions

This is the most common role; here is a detailed breakdown:

![en\_08-roles\_3](https://yifan2-500g.oss-cn-hangzhou.aliyuncs.com/crm-guide-mermaid/en_08-roles_3.png)

**Why are leads visible to everyone?**

* You need to see "unassigned" leads to proactively claim them
* Deduplication requires access to the full dataset to avoid duplicate entries
* You can view other people's leads but cannot modify them

![08-roles-2026-04-07-01-48-42](https://static-docs.nocobase.com/08-roles-2026-04-07-01-48-42.png)

**Why are customers restricted to your own?**

* Customers are core assets with clear ownership
* Prevents access to other reps' customer contact information
* When a transfer is needed, ask your manager to handle it

![08-roles-2026-04-07-01-50-37](https://static-docs.nocobase.com/08-roles-2026-04-07-01-50-37.png)

**² Contacts follow the customer**

The contacts you can see:

1. Contacts you are directly responsible for
2. **All** contacts under customers you own (even if created by someone else)

> Example: If you own the "Huawei" customer, you can see all contacts under Huawei, regardless of who entered them.

![08-roles-2026-04-07-01-51-26](https://static-docs.nocobase.com/08-roles-2026-04-07-01-51-26.png)

### Other Roles' Data Permissions

| Role | Full management access | Other data |
|------|----------------------|------------|
| Sales Manager | All CRM data | — |
| Executive | — | All read-only + export |
| Finance | Orders, payments, exchange rates, quotations | Other read-only |
| Marketing | Leads, lead tags, analytics templates | Other read-only |
| Customer Success Mgr | Customers, contacts, activities, comments, customer merge | Other read-only |
| Technical Support | Activities, comments (own only) | Can view contacts they are responsible for |
| Product | Products, categories, tiered pricing | Other read-only |

***

## Deduplication: Solving the "I Can't See It" Problem

Because customer data is isolated by ownership, you cannot see other reps' customers. But before entering a new lead or customer, you need to confirm **whether someone is already working on it**.

![en\_08-roles\_4](https://yifan2-500g.oss-cn-hangzhou.aliyuncs.com/crm-guide-mermaid/en_08-roles_4.png)

The deduplication page supports three types of searches:

* **Lead dedup**: Search by name, company, email, or phone
* **Customer dedup**: Search by company name or phone
* **Contact dedup**: Search by name, email, or phone

Search results show **who the owner is**. If a match exists, contact the corresponding colleague directly to coordinate and avoid conflicts.

![08-roles-2026-04-07-01-52-51](https://static-docs.nocobase.com/08-roles-2026-04-07-01-52-51.gif)

***

## FAQ

**Q: I can't see a certain page. What should I do?**

Your role does not have access to that page. If you need it for your work, contact an Admin to adjust your permissions.

**Q: I can see data but there's no edit/delete button?**

You have view-only permission for that data. This is usually because you are not the owner. Buttons for actions you don't have permission for are hidden entirely rather than shown as disabled.

**Q: I just joined a new department. When do the permissions take effect?**

Immediately. Refresh the page to see the new menus.

**Q: Can one person have multiple roles?**

Yes. Personal roles and department roles stack. For example, if you are personally assigned the "Sales Rep" role and also join the Marketing department, you hold the permissions of both the Sales and Marketing roles.

## Related Pages

* [System Overview & Dashboard](/solution/crm/guide/guide-overview.md) — How to use each dashboard
* [Lead Management](/solution/crm/guide/guide-leads.md) — Full lead workflow
* [Customer Management](/solution/crm/guide/guide-customers-emails.md) — Customer 360 view

# Application in UI

## Data Block Permissions

Visibility of data blocks in a collection is controlled by view action permissions, with individual configurations taking precedence over global settings.

For example, under global permissions, the "admin" role has full access, but the Orders collection may have individual permissions configured, making it invisible.

Global permission configuration:

![](https://static-docs.nocobase.com/3d026311739c7cf5fdcd03f710d09bc4.png)

Orders collection individual permission configuration:

![](https://static-docs.nocobase.com/a88caba1cad47001c1610bf402a4a2c1.png)

In the UI, all blocks in the Orders collection are not displayed.

Complete configuration process:

![](https://static-docs.nocobase.com/b283c004ffe0b746fddbffcf4f27b1df.gif)

## Field Permissions

**View**: Determines whether specific fields are visible at the field level, allowing control over which fields are visible to certain roles within the Orders collection.

![](https://static-docs.nocobase.com/30dea84d984d95039e6f7b180955a6cf.png)

In the UI, only fields with configured permissions are visible within the Orders collection block. System fields (Id, CreatedAt, LastUpdatedAt) retain view permissions even without specific configuration.

![](https://static-docs.nocobase.com/40cc49b517efe701147fd2e799e79dcc.png)

* **Edit**: Controls whether fields can be edited and saved (updated).

  Configure edit permissions for Orders collection fields (quantity and associated items have edit permissions):

![](https://static-docs.nocobase.com/6531ca4122f0887547b5719e2146ba93.png)

In the UI, only fields with edit permissions are shown in the edit action form block within the Orders collection.

![](https://static-docs.nocobase.com/12982450c311ec1bf87eb9dc5fb04650.png)

Complete configuration process:

![](https://static-docs.nocobase.com/1dbe559a9579c2e052e194e50edc74a7.gif)

* **Add**: Determines whether fields can be added (created).

  Configure add permissions for Orders collection fields (order number, quantity, items, and shipment have add permissions):

![](https://static-docs.nocobase.com/3ab1bbe41e61915e920fd257f2e0da7e.png)

In the UI, only fields with add permissions are displayed within the add action form block of the Orders collection.

![](https://static-docs.nocobase.com/8d0c07893b63771c428974f9e126bf35.png)

* **Export**: Controls whether fields can be exported.
* **Import**: Controls whether fields support import.

## Action Permissions

Individually configured permissions take the highest priority. If specific permissions are configured, they override global settings; otherwise, the global settings are applied.

* **Add**: Controls whether the add action button is visible within a block.

  Configure individual action permissions for the Orders collection to allow adding:

![](https://static-docs.nocobase.com/2e3123b5dbc72ae78942481360626629.png)

When the add action is permitted, the add button appears within the action area of the Orders collection block in the UI.

![](https://static-docs.nocobase.com/f0458980d450544d94c73160d75ba96c.png)

* **View**: Determines whether the data block is visible.

  Global permission configuration (no view permission):

![](https://static-docs.nocobase.com/6e4a1e6ea92f50bf84959dedbf1d5683.png)

Orders collection individual permission configuration:

![](https://static-docs.nocobase.com/f2dd142a40fe19fb657071fd901b2291.png)

In the UI, data blocks for all other collections remain hidden, but the Orders collection block is shown.

Complete example configuration process:

![](https://static-docs.nocobase.com/b92f0edc51a27b52e85cdeb76271b936.gif)

* **Edit**: Controls whether the edit action button is displayed within a block.

![](https://static-docs.nocobase.com/fb1c0290e2a833f1c2b415c761e54c45.gif)

Action permissions can be further refined by setting the data scope.

For example, setting the Orders collection so users can only edit their own data:

![](https://static-docs.nocobase.com/b082308f62a3a9084cab78a370c14a9f.gif)

* **Delete**: Controls whether the delete action button is visible within a block.

![](https://static-docs.nocobase.com/021c9e79bcc1ad221b606a9555ff5644.gif)

* **Export**: Controls whether the export action button is visible within a block.

* **Import**: Controls whether the import action button is visible within a block.

## Association Permissions

### As a Field

* The permissions of an association field are controlled by the field permissions of the source collection. This controls whether the entire association field component is displayed.

For example, in the Orders collection, the association field "Customer" only has view, import, and export permissions.

![](https://static-docs.nocobase.com/d0dc797aae73feeabc436af285dd4f59.png)

In the UI, this means the "Customer" association field will not be displayed in the add and edit action blocks of the Orders collection.

Complete example configuration process:

![](https://static-docs.nocobase.com/372f8a4f414feea097c23b2ba326c0ef.gif)

* The permissions for fields within the association field component (such as a sub-table or sub-form) are determined by the permissions of the target collection.

When the association field component is a sub-form:

As shown below, the "Customer" association field in the Orders collection has all permissions, while the Customers collection itself is set to read-only.

Individual permission configuration for the Orders collection, where the "Customer" association field has all field permissions:

![](https://static-docs.nocobase.com/3a3ab9722f14a7b3a35361219d67fa40.png)

Individual permission configuration for the Customers collection, where fields have view-only permissions:

![](https://static-docs.nocobase.com/46704d179b931006a9a22852e6c5089e.png)

In the UI, the "Customer" association field is visible in the Orders collection block. However, when switched to a sub-form, the fields within the sub-form are visible in the details view but are not displayed in the add and edit actions.

Complete example configuration process:

![](https://static-docs.nocobase.com/932dbf6ac46e36ee357ff3e8b9ea1423.gif)

To further control permissions for fields within the sub-form, you can grant permissions to individual fields.

As shown, the Customers collection is configured with individual field permissions (Customer Name is not visible and not editable).

![](https://static-docs.nocobase.com/e7b875521cbc4e28640f027f36d0413c.png)

Complete example configuration process:

![](https://static-docs.nocobase.com/7a07e68c2fe2a13f0c2cef19be489264.gif)

When the association field component is a sub-table, the situation is consistent with that of a sub-form:

As shown, the "Shipment" association field in the Orders collection has all permissions, while the Shipments collection is set to read-only.

In the UI, this association field is visible. However, when switched to a sub-table, the fields within the sub-table are visible in the view action but not in the add and edit actions.

![](https://static-docs.nocobase.com/fd4b7d81cdd765db789d9c85cf9dc324.gif)

To further control permissions for fields within the sub-table, you can grant permissions to individual fields:

![](https://static-docs.nocobase.com/51d70a624cb2b0366e421bcdc8abb7fd.gif)

### As a Block

* The visibility of an association block is controlled by the permissions of the target collection of the corresponding association field, and is independent of the association field's permissions.

For example, whether the "Customer" association block is displayed is controlled by the permissions of the Customers collection.

![](https://static-docs.nocobase.com/633ebb301767430b740ecfce11df47b3.gif)

* The fields within an association block are controlled by the field permissions in the target collection.

As shown, you can set view permissions for individual fields in the Customers collection.

![](https://static-docs.nocobase.com/35af9426c20911323b17f67f81bac8fc.gif)
