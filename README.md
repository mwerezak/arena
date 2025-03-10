# arena
RPG combat engine inspired by RuneQuest

A somewhat old project that I'm not working on anymore. I'm releasing the source code to the public in case anyone finds it useful.

Right now it's just a demonstration of the engine, you can setup a pair of NPCs to fight each other and read the combat logs.

Produces output like the following (with some after-the-fact formatting):
```
Gnoll Warrior (797sp)
Leather Cuirass
Battleaxe
Medium Shield

Orc Barbarian (1525sp)
Leather Helmet
Leather Hide Armor
Iron Brigandine Cuirass
Medium Shield
Battleaxe

Tick: 0 Action Queue:
<MeleeCombatAction owned by: Gnoll Warrior, started: 0, remaining: 100>
<MeleeCombatAction owned by: Orc Barbarian, started: 0, remaining: 111>

[Initiative] Gnoll Warrior vs Orc Barbarian RESULT: 5+8=13 vs 3+4=7 Gnoll Warrior takes initiative!
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 16+3=19 vs 14+4=18 SUCCESS (crit level: 0)
Orc Barbarian attempts to block with Medium Shield!
[Opposed Contest] Shields vs Axes RESULT: 12+4=16 vs 16+3=19 FAIL (crit level: 1)
Gnoll Warrior strikes Orc Barbarian in the Left Arm for 7 damage: Battleaxe (Hack)!
Orc Barbarian suffers an injury to the Left Arm.
[Opposed Contest] Endurance vs Axes RESULT: 14+3=17 vs 16+3=19 FAIL (crit level: 0)
Orc Barbarian drops the Medium Shield.
Orc Barbarian is wounded for 4.0 damage (armour 1).
Orc Barbarian health: 6/10
[Test] Acrobatics RESULT: 14+2(+1)=17 vs 10 SUCCESS (crit level: 0)

Tick: 100 Action Queue:
<MeleeDefendAction owned by: Orc Barbarian, started: 100, remaining: 0>
<MeleeCombatAction owned by: Gnoll Warrior, started: 100, remaining: 100>

Tick: 100 Action Queue:
<MeleeCombatAction owned by: Gnoll Warrior, started: 100, remaining: 100>
<MeleeCombatAction owned by: Orc Barbarian, started: 100, remaining: 111>

[Initiative] Gnoll Warrior vs Orc Barbarian RESULT: 1+8=9 vs 2+5=7 Gnoll Warrior takes initiative!
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 11+3=14 vs 14+4=18 FAIL (crit level: 0)
next_turn()

Tick: 200 Action Queue:
<MeleeDefendAction owned by: Orc Barbarian, started: 200, remaining: 0>
<MeleeCombatAction owned by: Gnoll Warrior, started: 200, remaining: 100>

Tick: 200 Action Queue:
<MeleeCombatAction owned by: Gnoll Warrior, started: 200, remaining: 100>
<MeleeCombatAction owned by: Orc Barbarian, started: 200, remaining: 111>

[Initiative] Gnoll Warrior vs Orc Barbarian RESULT: 5+8=13 vs 4+5=9 Gnoll Warrior takes initiative!
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 16+3=19 vs 11+4=15 SUCCESS (crit level: 1)
(Gnoll Warrior) !Critical Effect - Disrupt Opponent!
Gnoll Warrior strikes Orc Barbarian in the Right Leg for 5 damage: Battleaxe (Hack)!
Orc Barbarian suffers an injury to the Right Leg.
[Opposed Contest] Endurance vs Axes RESULT: 12+3=15 vs 16+3=19 FAIL (crit level: 1)
Orc Barbarian can no longer stand!
Orc Barbarian is wounded for 2.7 damage (armour 1).
Orc Barbarian health: 3/10

Tick: 300 Action Queue:
<MeleeDefendAction owned by: Orc Barbarian, started: 300, remaining: 0>
<MeleeCombatAction owned by: Gnoll Warrior, started: 300, remaining: 100>

Tick: 300 Action Queue:
<MeleeCombatAction owned by: Gnoll Warrior, started: 300, remaining: 100>
<DisruptedAction owned by: Orc Barbarian, started: 300, remaining: 148>
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 11+3=14 vs 14+4(-2)=16 FAIL (crit level: 0)

Tick: 400 Action Queue:
<MeleeDefendAction owned by: Orc Barbarian, started: 400, remaining: 0>
<MeleeCombatAction owned by: Gnoll Warrior, started: 400, remaining: 100>

Tick: 400 Action Queue:
<MeleeCombatAction owned by: Gnoll Warrior, started: 400, remaining: 100>
<MeleeCombatAction owned by: Orc Barbarian, started: 400, remaining: 111>

[Initiative] Gnoll Warrior vs Orc Barbarian RESULT: 5+8=13 vs 3+5=8 Gnoll Warrior takes initiative!
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 8+3=11 vs 13+4(-2)=15 FAIL (crit level: 0)

Tick: 500 Action Queue:
<MeleeDefendAction owned by: Orc Barbarian, started: 500, remaining: 0>
<MeleeCombatAction owned by: Gnoll Warrior, started: 500, remaining: 100>

<MeleeCombatAction owned by: Gnoll Warrior, started: 500, remaining: 100>
<MeleeCombatAction owned by: Orc Barbarian, started: 500, remaining: 111>
[Initiative] Gnoll Warrior vs Orc Barbarian RESULT: 5+8=13 vs 5+5=10 Gnoll Warrior takes initiative!
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 14+3=17 vs 17+4(-2)=19 FAIL (crit level: 0)

Tick: 600 Action Queue:
<MeleeDefendAction owned by: Orc Barbarian, started: 600, remaining: 0>
<MeleeCombatAction owned by: Gnoll Warrior, started: 600, remaining: 100>

Tick: 600 Action Queue:
<MeleeCombatAction owned by: Gnoll Warrior, started: 600, remaining: 100>
<MeleeCombatAction owned by: Orc Barbarian, started: 600, remaining: 111>

[Initiative] Gnoll Warrior vs Orc Barbarian RESULT: 10+8=18 vs 7+5=12 Gnoll Warrior takes initiative!
Gnoll Warrior attacks Orc Barbarian at Medium distance: Battleaxe (Hack) vs Battleaxe (Hack)!
[Opposed Contest] Axes vs Axes RESULT: 17+3=20 vs 14+4(-2)=16 SUCCESS (crit level: 1)
(Gnoll Warrior) !Critical Effect - Choose Hit Location: Head and Neck!
Gnoll Warrior strikes Orc Barbarian in the Head and Neck for 7 damage: Battleaxe (Hack)!
Orc Barbarian suffers an injury to the Head and Neck.
[Opposed Contest] Endurance vs Axes RESULT: 14+3=17 vs 17+3=20 FAIL (crit level: 0)
Orc Barbarian is wounded for 6.0 damage (armour 3).
Orc Barbarian is seriously wounded!
[Opposed Contest] Endurance vs Axes RESULT: 10+3=13 vs 17+3=20 FAIL (crit level: 1)
Orc Barbarian is incapacitated!
Orc Barbarian health: -3/10
```
