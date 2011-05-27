Werewolf Tracker
================

This is a simple ap designed to keep track of who votes for whom in an online game of werewolf as played on somewhere like the [Giant In The Playground](http://www.giantitp.com/forums/) forums.

This consists of a Google AppEngine application, very roughly written, that tracks the players and the votes they made, and a chrome browser plugin that when browsing the forum adds a javascript button to attempt to scrape a vote from a forum post, and prefill a form that can submit to the webapp.

Usage
-----

This was never really designed for other people to use, but once installed and working, from the front page you can create a new game or select a current game.  When you select a game, the web application stores the most recently accessed game as the "current" game, so the plugin will submit votes to that game.

Once a game is created, you can simply start adding votes, and act of voting using the chrome plugin should go via the AutoVote controller, and create the voter and votee (source and target) of the vote in the game.  This means that if somebody mispells a targets name it will automatically create a new player.

The create vote form in the webapp itself has a drop down selector so you could manually create each player and select them from the drop down list, which will create votes.

Most games of Werewolf are played in Day/Night cycles, entering a game phase into the current turn box and selecting change turn will set the current turn.  This can be used to go forward to Day 2, creating a brand new list of votes, or to navigate forwards and backwards through the days if you want to refer to older data.

Todo
----

I've certainly written better code, this was built purely as a replacement to a spreadsheet I was keeping for a game, and I added features as it went, here's a basic list of raw requirements that I've never managed to get round to doing

- Make it look nice, it's grid-based, but I never put any real styling on it
- Security, currently it's possible for anyone to submit a vote, without any authentication
- Better Edit/Delete workflow, I added edit and delete to fix mistakes where I was in 2 games at once, but it's painful to do any real management
- Performance - None of the datastore operations were designed with scalability or performance in mind, I just built it for 1 user
- Consistency - There was a period where players changing their votes could cause inconsistent counting, which I fixed by running the fixup handler when I needed to read stats.  I think I fixed that, but there might be other consistency issues
- Find a reason to use it

How about some actual new features that I was planning?

- Keep track of who died in night phases
- Game phase navigation (i.e. next previous buttons)
- Track more player information, i.e. known state (werewolf, villager, role etc), allegience, notes etc.
- Add analytics per user, i.e. number of times voted for lynchee, number of changes, etc.