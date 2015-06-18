# Changelog

## 0.1.2

## 0.1.1 (June 18, 2015)
  * `dusty setup` now looks for your nginx config in all 3 default locations
  * `dusty status` has been added.  Will give a dump of activated apps, services and libs.  Will also tell you if their is a container associated with them
  * changed how we are treating specs.
    * In app spec `commands.once`, `commands.always` and `scripts.command` value are now lists and not strings
    * In lib spec `install` value is now a list and not a string
    * In test spce `once` and `suites.command` are now lists and not strings

## 0.1.0 (June 15, 2015)
  * Initial release
