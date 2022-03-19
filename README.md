![DCSTerminal-Banner](https://user-images.githubusercontent.com/85963782/159130727-c8536e41-f8b3-45d1-b721-454ea6c9efa5.png)
<hr>
This program will automatically finish a datacamp course in minutes using a hacker-esque terminal! It has a few important commands and settings to know about, so either watch <a href="https://github.com/Traptricker/DCS_Terminal/edit/master/README.md">this</a> video, or continue reading this readme. 

# How to use it
Go to ![image](https://user-images.githubusercontent.com/85963782/150718639-bec6b20b-f788-4d28-9315-25d33103b6ca.png) and download the latest release's installer (should be an exe.) Once downloaded, run the installer and if a popup appears saying "Windows protected your PC", click `more info` then `Run anyway`. Click `next` on the installer (making a desktop shortcut is recommended) then click `install` and `finish`.

If everything worked properly, when you launch the application chrome should launch and you should see this window:

![image](https://user-images.githubusercontent.com/85963782/159132401-c8fb0906-40a6-42ab-8ae3-7d2b2e42205b.png)

## Follow these steps to solve a Datacamp course
1. Open a browser and log into Datacamp, then find the course you want to be solved and open the course so that you are at one of the problems/exercises. Now, copy the link of that page, it should look something like `https://campus.datacamp.com/courses/supervised-learning-with-scikit-learn/classification?ex=1` (if it has `ex=` a number, you've got the right link)
2. Next, launch DCS Terminal and once you see ![image](https://user-images.githubusercontent.com/85963782/159138489-a51fdbbf-43de-45c2-8f0d-8574f52f5419.png), type: `setcreds YourDatacampEmail@email.com YourDatacampPassword` and press enter. *This will store your login information, so next time you want to use the terminal, you won't have to enter it again.*
3. Type `login` and wait for the chrome tab to be fully logged into Datacamp. If the login fails, try running the command again.
4. Finally, with the link you copied earlier, type: `solvecourse TheLinkYouCopied`.
5. Sit back and relax! You can have the terminal and the chrome tab minimized and continue to use your computer, try not to use copy and paste too much while it is running as the terminal copies the answers, then pastes them into Datacamp.

**If you did everything right, your terminal should look like this and the course should be getting solved.**
![unknown](https://user-images.githubusercontent.com/85963782/159138939-da3297be-6b28-4287-b24e-da1e4530ff11.jpg)


# Important to Know
- **This program will not work for courses on spreadsheets**
- **If you get an error that says something about chromedriver and or its version, make sure you have chrome updated to version 99**

# Motivation
We are both very passionate about programming and learning new things, but we shared a hatred of datacamp. When we found out that all of the answers to the exercises were in the page's source code, we new we had to exploit such an obvious vulnerability. Its about the principle! Not about cheating on Datacamp! We made this in order to learn more about websites, Selenium, and the Terminal.

# Extra Bugs in Datacamp
Datacamp has a lot of exploits, here are some of the biggest ones:
- For a normal exercise, if you click `Take Hint` then `Show Answer` you can copy the answer, refresh the page, and lose no XP
- For an exercise with multiple parts, if you disconnect your computer from the internet, you can get all of the answers through `Take Hint` then `Show Answer`, refresh the page, turn your internet back on, and lose no XP
- For any exercise, if you right click the page and click `View Page Source`, you can find all of the module's questions and answers through ctrl + f
- For any exercise, if you right click the page and click `Inspect Element`, click `Network` in the opened window, filter to `Fetch/XHR` then click `Take Hint` then `Show Answer`. Now, in the window Inspect Element opened up, under `Name` you should see `get_solution`. Click on that and voila! You now can see the API to get any answer on Datacamp. (https://campus-api.datacamp.com/api/exercises/1133452/get_solution, change `1133452` to your current exercise ID)

# Frameworks, Tools, and Libraries used
- [Selenium](https://www.selenium.dev/documentation/)
- [Undetected-Chromedriver](https://pypi.org/project/undetected-chromedriver/2.1.1/)


MIT © [Traptricker](https://traptricker.github.io/) & [iBrushC](https://github.com/iBrushC)
