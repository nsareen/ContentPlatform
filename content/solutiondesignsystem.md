1. Foundations

1.1 Color Palette

Define semantic tokens and raw color values for backgrounds, text, borders, and interactive elements.

Token

Usage

Value

Primary.Purple

Primary buttons, headers, active states

#6D3BEB

Primary.PurpleLight

Hover states, highlights

#8B63F9

Primary.PurpleDark

Active states, focus rings

#5A26B8

Secondary.Blue

Secondary actions, links

#007AFF

Secondary.BlueLight

Hover states for secondary actions

#3EAFFF

Text.Primary

Main body text

#1E2334

Text.Secondary

Subdued text (e.g., labels, metadata)

#475569

Text.Tertiary

Placeholder text, hints

#94A3B8

Background.Default

Page background

#FFFFFF

Background.Surface

Cards, modals, panels

#F8FAFC

Background.Light

Elevated surfaces, rows

#FFFFFF

Border.Default

Field and divider borders

#E2E8F0

Border.Light

Subtle dividers

#F1F5F9

Feedback.Success

Success messages, positive badges

#10B981

Feedback.Warning

Warnings, caution badges

#F59E0B

Feedback.Error

Error messages, negative badges

#EF4444

1.2 Typography

All text uses the Inter family (fallback sans-serif).

Style

Size

Line Height

Weight

Token

Heading 1

24px

32px

600

font.h1

Heading 2

20px

28px

600

font.h2

Heading 3

16px

24px

500

font.h3

Body

14px

20px

400

font.body

Caption

12px

16px

400

font.caption

1.3 Spacing & Layout

Based on a 4px base unit. Use multiples for margins, padding, and grids.

Scale

Value

XSmall

4px

Small

8px

Medium

16px

Large

24px

XL

32px

XXL

40px

Grid: 8px-based column grid for layout.

1.4 Elevation & Shadows

Token

CSS Shadow

shadow.sm

0px 1px 2px rgba(0, 0, 0, 0.05)

shadow.md

0px 4px 8px rgba(0, 0, 0, 0.10)

shadow.lg

0px 8px 16px rgba(0, 0, 0, 0.15)

1.5 Border Radius

Token

Value

radius.sm

4px

radius.md

8px

radius.lg

16px

2. Component Guidelines

Reusable patterns, states, and anatomy.

2.1 Buttons

Type

Background

Text Color

Border

Hover / Active

Primary

Primary.Purple

#FFFFFF

none

Primary.PurpleLight

Secondary

#FFFFFF

Primary.Purple

1px solid Primary.Purple

background #F8F9FE, text darken

Tertiary/Link

transparent

Secondary.Blue

none

Secondary.BlueLight

Disabled

#F1F5F9

#94A3B8

none

cursor not-allowed

Sizes:

Small: 32px height, 8px 12px padding

Medium: 40px height, 12px 16px padding

Large: 48px height, 16px 24px padding

2.2 Form Inputs

Height: 40px

Padding: 8px 12px

Border: 1px solid Border.Default

Border Radius: radius.sm

Focus State: border-color: Primary.Purple; box-shadow: 0 0 0 2px rgba(109, 59, 235, 0.2); outline: none;

Disabled: background: #F1F5F9; color: Text.Tertiary; cursor: not-allowed;

Variants: Text field, Textarea (multi-line), Dropdown, Checkbox, Radio.

2.3 Modals & Dialogs

Max Width: 600px

Padding: Large (24px)

Header: background Primary.Purple, text #FFFFFF, padding Medium (16px)

Border Radius: radius.lg

Backdrop: rgba(0,0,0,0.2)

Close Icon: top-right, 16px size, Text.Light color

2.4 Cards & Panels

Background: Background.Surface

Border Radius: radius.md

Shadow: shadow.sm

Padding: Medium (16px)

2.5 Tables & Lists

Row Height: 48px

Divider: 1px solid Border.Light

Hover: background: #F5F7FF

Selected: background: #EEF2FF; border-left: 4px solid Primary.Purple

2.6 Navigation Bar & Sidebar

Topbar Height: 56px; background #FFFFFF; shadow shadow.sm

Sidebar Width: 240px; background #FFFFFF; border-right 1px solid Border.Light

Active Nav Item: text Primary.Purple, background #F5F0FF

3. Iconography

Library: Use 24px grid, stroke icons (2px stroke) in Text.Secondary.

Active/Selected: fill Primary.Purple or stroke in Primary.Purple.

Interactive: hover stroke Text.Primary, tap scale 0.95.

4. Accessibility & Motion

Contrast: All text meets WCAG AA (4.5:1 for normal, 3:1 for large text).

Focus: Clear focus rings on interactive elements.

Motion: Use subtle transitions (0.2s ease-in-out) for hover/focus.