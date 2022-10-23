# Reminders

Just to remember some decisions...

## Part

### stock_min

Desired minimum stock_level

### stock_low()

Returns true if stock_level < stock_min

## Attachment

The Attachment element does not hold the files itself. Those are stored in fileDB and are referenced by Attachment _id. Over the API this can be done by the endpoint AttachmentFile.

## ParameterClass

### first_level (boolean)

if set to true the parameter is meant to be displayed besides the other main attributes/parameters of the part (this might be in the detail(edit) or list views)

defaults to false

### second_level (boolean)

if set to true the parameter is meant to be displayed on some kind of info-box when the corrensponding part is selected

defaults to false

### always (boolean)

if set to true this ParameterClass is always displayed on all parts without the need of the user to add it explicitly.

defaults to false