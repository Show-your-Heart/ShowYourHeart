# Changelog

All notable changes to this project will be documented in this file.

## [0.4.0] - 2026-08-06

### 🚀 Features

- Automatically add network on organization creation (#516)
- Add info text on external surveys csv import (#522)
- Add network managed field to Organizations (#520)
- Add a confirmation message before submitting the survey (#521)
- Display field managed_by on Networks (#524)
- Add smtp from_email helper function
- Add field from_email
- Define from_email field when sending emails
- Add timeout and error check when sending email
- Sites & Multi-domain configuration

### 🐛 Bug Fixes

- Allow to edit group auth permissions on superadmin (#515)
- Update network permissions (#528)

### ⚙️ Miscellaneous Tasks

- Update CHANGELOG
- Update translations

## [0.3.0] - 2026-07-09

### 🚀 Features

- Add favicon
- Add support for null operator in expressions
- Put indicators set description inside the information button to match fields UI
- Add admin panel button in header

### 🐛 Bug Fixes

- Round totals of type decimal in tables
- Translate indicators set add button
- Count null table cell as 0 in totals calculation
- Update dependent indirect field validation errors
- Add animated transition in group field error display to avoid  ignored click on "fill with zeros" button in some cases
- Change sets title styles to match indicators styles
- Hide deep dependent sets
- Update dependent indicators both when field is valid and invalid
- When a set in the survey had more than one isntance all sets where set to have the same number of instances
- Init fields after indicators store has finished initializing
- Properly initialize indicators in sets inside the indicators store
- Update field validation when setting NA
- Display networks data only, show indicators, hide surveys from other networks and fix users filer
- Filter admin home surveys and registration requests to display correct data
- Make survey inert (readonly) after submission, closes #494
- Prevent implicit submission of form on enter key-press
- Align text start in method fill sidebar menu
- Don't set NA/hide dependent indicators when an indicator is set to NA/hidden
- Csv import and display error messages
- Zip codes not appearing for network admins (#507)
- Update dependencies recursively and reuse updateNotApplicable function of fields to avoid errors with stored data when the field has been checked and unchecked as NA
- Allow the use of conditional expressions containing references to sets in indicators that doesn't belong to a set
- Set opacity for readonly indirect indicators of type boolean and radio button
- Properly update indirect indicators after evaluating forumla reusing update function from field
- Allow to control the display of field errors when updating NA to avoid initial errors when dependencies are displayed after editing a field
- Clear lists, tables and gendered fields when set to NA
- Add multiple parent nodes to update indicator properly

### 🚜 Refactor

- Duplicate updateShow call, remove hide param to avoid it
- Implement queue strategy to avoid duplicated calculations in dependent indicators

### ⚙️ Miscellaneous Tasks

- Bump tar from 7.5.11 to 7.5.19 (#511)

## [0.2.0] - 2026-06-08

### 🚀 Features

- Review balances add sorting by date
- Add success screen when submitting a method
- Fix fill group lists with zeros, add color button, hide validate button if no validation and add visual feedback to validate button click
- Make indicator dependencies visible in admin panel
- Search indicator result by indicator code
- Allow to hide/show section title from admin settings

### 🐛 Bug Fixes

- On registration the Allow infographics to be public was mandatory when it shouldn't
- Error loading values in expression, check if indicator to be loaded belongs to set
- Indirect indicator description not clickable, remove pointer-event-none in label
- Formated links in sections description and bullet points in indicators description
- Add indicator dependencies only once
- Ignore not found dependencies
- Add quotes to strings inside indicators expressions
- Set border red on input field error
- Display indirect indicators errors
- Fix suvey stats card info
- Null value in string inputs
- Assure well-formed instanceId when updating dependent indicators NA result
- Properly store indicator results adding support for indicators sets and fix problem with tables in survey card stats function
- When saving the survey do not redirect to the success message

### ⚙️ Miscellaneous Tasks

- Update changelog and readme

## [0.1.0] - 2026-05-12

### 🚀 Features

- Change docker image build strategy to allow live reload of templates
- Update login view and overwrite some admin templates to allow the use of custom components
- User and admin sidebar and header (wip)
- Create a separated admin site for superadmins and refactor sidebar closes #45
- Upgrade to tailwind4 to allow unfold integration with custom styles using tw classes
- Add static app logo
- Update admin sidebar with new models
- Add survey stats
- Add signup success view
- Update header to remove avatar dropdown menu
- Imrpove method fill view and use custom widget for input text fields
- Update home view ui, refactor method_fill view and add organization object when submitting method reply
- Add gov admin home page
- Rename project_id field to code
- Indicators client state management and reactivity
- Update some field types to use the state management
- Add support for users to save and automatic load of initial values in method forms
- Add gendered field interactivity
- Add previous section button
- Add interactive sidebar section status
- Update methods sidebar name
- Add register requests view
- Add edit and delete organization buttons functionality
- Improve gov admin menu
- Accept and reject buttons
- Add  dynamic number of pending registration requests on admin index page
- Client notification toasts system
- Home secondary meny UI refinement
- Project selection and creation drawers
- Add regular user to load dev data
- Fine-tune review balances view
- Add edit survey in balance review page
- Django-import-export integration and implementation for indicator model
- Add remaining questions modal to users method fill view
- Add survey status to govadmin balance review view
- Option value is list item id and list item value is only used in expressions (condition, formula, validation)
- Add gendered fields expressions support
- Add support for list indicators with the creation of group indicators
- Add generic tables support
- Add support for 'val', 'true' and 'false' keywords
- Add support for list, table rows and table columns total values in expressions
- Add group item validation on blur and group field validation on submit, rename parseExpression parameter 'code' to 'val' to match val keyword
- Add support for previous campaign as placeholders
- Add html content to indicators name and help drawer
- Export organizations by region1
- Add import/export functionality to lists, list items, groups and group items and add related instances with custom fields available for them and for indicator's topics, list, group and group2
- Add logical operators to indicators expressions
- Add method and section models to import/export
- Allow indirect indicators to be displayed
- Add section title before fields in method fill
- Add automatic group totals
- Hide external suverys button if method doesn't have
- Add description to section model
- Add "fill with 0's" button
- Detect "copy" formula in indict indicators and add support for types with options.
- Add different color in field code tag to differentiate direct and indirect indicators
- Add support for boolean expressions in boolean indirect indicator's formula
- Add support for indicators sets
- Enable import of indicators_sets and add indicators_sets_code column  to sections and methods when importing
- Display boolean field error
- Display message on external survey message sending (#443)
- Add conditional sets
- Ignore missing indicator dependencies and alert in the client console
- Add email templates for balance status changes and registration (#455)
- Add translations
- Create set operator to calculate the total of all set indicator instances
- Add texts on nav menu
- On project creation add start date tooltip (#464)

### 🐛 Bug Fixes

- Command no longer using env directly, and added more logging messages.
- Add media and admin scripts to fix many to many fields on admin ui, closes #159
- Logout background ui fix in main header dropdown
- Properly layout add button in admin ui, closes #160
- Add creation button in admin lists
- Change logo color based on header color
- Remove dark theme styles
- Direct indicators were hidden if conditional show had no condition set, indirect indicators where disabled and its value was not stored
- Missing styles in views and cookies banner
- Add info icon on inputs only if description is available
- Raise error when registring with existing contact closes #107
- Remove cookies banner from logged in pages
- Profile details save button fixed
- Update icon component API
- Organization model was overwritten and rejected registration request email text was wrong
- Remove unmerged lines, closes 281
- Closes #265
- Disable dark mode of unfold
- Base-field component was moved to a new folder, tag name needed update
- Unset campaign_id in method fill view (wip)
- Fine-tune position of tabs and add button and min sice of change form
- Update field when unchecked NA checkbox
- ValidateSurvey return value error
- Multi-answer indicators checkboxes state
- Make invisible field NA
- Gendered x-effect triggered uninitialized error due to dependant indicators, refactor all field types to remove unnecessary x-effect since is triggered by click event in base field (missing support for all types of fields)
- Update radio field type to support new refactor of list items
- Checkbox field type was missbehaving whent the checkbox (not the label) was clicked, disabled checkbox clicl event to avoid it
- Pointer event in radiobutton fields
- Fix load_dev_data script and display condition for group indicators
- Radio fields bad initial value
- Render validation error only once per list/table
- Mr comments
- Display table field error
- Set initial value to null to allow placeholders to be displayed
- Method selection field in register form
- Initialized placeholder if null
- Validation without expression for fields with options was missing and dropdown didnt have errors display
- Mark dependant fields as NA recursevly
- Add models to admin menu, remove network model permissions for network admin, remove it from network admin menu and update models permissions to include groups
- Broken layout and styles in privacy policy
- Show indicators name as processed html not raw
- Refactor duplicated code when preparing method fill context for both users and admins to fix review balance problems
- Group indicators label layout
- Remove bad fields from section resource class
- Logical value of evaluateExpression in validation
- Properly init survey state in review balance view
- Hide modal event missing argument
- Remove bad fields from section resource class
- Add empty option as default to force user to select one
- Scroll to top on method section click
- _total operator broken for lists and tables, refactor and fix
- Improve help drawer size
- Imrpove group totals display in admin
- Set indirect indicator as readonly instead of disabled to store it
- Wrong dynamic type that is setted in server
- Better UI for indicators label and title
- Imposible to update indicators (#414)
- Diferentiate dependant expression in indicators to triger only the required one (e.g. only condition, not condition and formula)
- Dropdown indicators with options with value 0
- Remove unused @submit from form that was loging an error in console
- Correct colors in survey stats card
- Load stored value of boolean field and properly load it in indicators expressions
- Submit survey button error
- Fixed checkbox indicator validation
- Radio buttons type missing validation,initial load and option id storage
- Survey review, fix edit survey and survey info buttons
- Hide number input's buttons
- Gendered field and lists totals and predefined suffixes
- Round to two decimals
- Use '%' symbol instead of word in units
- Escape apostroph on sections
- External surveys. add campaign id (#420)
- Make method indicators_sets nullable
- Properly set blank property in method indicators_set field
- Add related name to group items
- Add related_name to list items
- Typo in js expression in NA of group base field
- Load indicators_sets in subsections
- Remove duplicate load of sections in method fill
- Conditional instanceID typo in update dependant indicators na
- Update survey stats helper
- Properly load initial values
- Properly load values in expressions
- Add dependant validation and groups validation button
- External survey save and get by token (#437)
- Group indicators lists error in totals
- Load initial values of tables
- Load initial value of gendered fields
- Update dependeant indicator NA
- Fill survey errors modal display sections title
- Hide empty subsections
- Properly implement change events in dropdowns, radio buttons and checkboxes lists
- Add for in labels of group fields
- Add deep dependant indicators
- Error on opening project balance (#457)
- Translated urls errors
- Ignore empty indicator set non-instance result
- Check if dependent condition has indicators set when no indicator is found

### 🚜 Refactor

- Loaddevdata moved from users to project.
- Superuser creation included in loaddevdata command, and auto_superuser command removed.
- Start componentization of UI with django-cotton
- Change custom template handling and improve admin templates
- Change help tooltip to  drawer
- Move view definition to views.py
- Move email templates to HTML files and load them through a command
- Move forms components into methods folder
- Componentize search form of balance review
- Remove flowbite imported twice in default layout
- Reorder info button in field to be by the question title
- Update load_dev_data command name
- Move indicators state to indicatores store to make it globally available
- Add section Data structure and global sections state management, remove unnecesary methods and create fron-ent components for sections and subsections, fix navigato to error field

### 📚 Documentation

- Commands section adapted to changes.
- Developer's guide linked.

### ⚙️ Miscellaneous Tasks

- Install django-cotton, update tailwind config and add node_modules to gitignore
- Add flowbite locally
- Remove deprecated code, project choose modal in the home view
- Remove dark theme css classes
- Fix lint
- Remove logs
- Remove unused log
- Remove comments
- Store maps of indicators to reduce the use of .find and .findIndex
- Add changelog

### Fix

- Node modules paths in tailwind config.

<!-- generated by git-cliff -->
