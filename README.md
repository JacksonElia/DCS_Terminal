![DCSTerminal-Banner](https://user-images.githubusercontent.com/85963782/159130727-c8536e41-f8b3-45d1-b721-454ea6c9efa5.png)
<hr>
This program will automatically finish a datacamp course in minutes using a hacker-esque terminal! It has a few important commands and settings to know about, so either watch <a href="https://github.com/Traptricker/DCS_Terminal/edit/master/README.md">this</a> video, or continue reading this readme.

# How to use it
Go to ![image](https://user-images.githubusercontent.com/85963782/150718639-bec6b20b-f788-4d28-9315-25d33103b6ca.png) and download the latest release's installer (should be an exe.) Once downloaded, run the installer and if a popup appears saying "Windows protected your PC", click `more info` then `Run anyway`. Click `next` on the installer (making a desktop shortcut is recommended) then click `install` and `finish`.

If everything worked properly, when you launch the application you should see this window:

# Motivation
We are both very passionate about programming and learning new things, but we shared a hatred of datacamp. When we found out that all of the answers to the exercises were in the page's source code, we new we had to exploit such an obvious vulnerability. Its about the principle! Not about cheating on Datacamp! We made this in order to learn more about websites, Selenium, and the Terminal.

# Extra Bugs in Datacamo
Datacamp has a lot of exploits, here are some of the biggest ones
- For a normal exercise, if you click `Take Hint` then `Show Answer` you can copy the answer, refresh the page, and lose no XP
- For an exercise with multiple parts, if you disconnect your computer from the internet, you can get all of the answers through `Take Hint` then `Show Answer`, refresh the page, turn your internet back on, and lose no XP
- For any exercise, if you right click the page and click `View Page Source`, you can find all of the module's questions and answers through ctrl + f
- For any exercise, if you right click the page and click `Inspect Element`, click `Network` in the opened window, filter to `Fetch/XHR`

# Frameworks, Tools, and Libraries used
- [Selenium](https://www.selenium.dev/documentation/)
- [Undetected-Chromedriver](https://pypi.org/project/undetected-chromedriver/2.1.1/)


MIT © [Traptricker](https://traptricker.github.io/) & [iBrushC](https://github.com/iBrushC)
