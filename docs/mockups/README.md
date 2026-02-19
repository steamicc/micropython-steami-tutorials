# steami\_screen — Visual Report

**15 tutorials** · **15/15 PASS** (SSIM ≥ 0.85) · Generated 2026-02-19

Each card shows the SVG reference mockup alongside the Pillow simulation, with the SSIM similarity score.


<table>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/01_temperature/main.py'>Temperature</a></strong><br><br>
      <img src='01_temperature.svg' width='180' title='SVG reference'>&nbsp;<img src='01_temperature_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.value(temp, unit='C')</code><br>
      <sub>Reads temperature from HTS221 sensor</sub><br>
      <sub>SSIM&nbsp;0.8762&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/02_battery/main.py'>Battery</a></strong><br><br>
      <img src='02_battery.svg' width='180' title='SVG reference'>&nbsp;<img src='02_battery_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.bar(soc)</code><br>
      <sub>Battery state of charge from BQ27441 gauge</sub><br>
      <sub>SSIM&nbsp;0.9023&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/03_comfort_dual/main.py'>Comfort (dual)</a></strong><br><br>
      <img src='03_comfort_dual.svg' width='180' title='SVG reference'>&nbsp;<img src='03_comfort_dual_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.value() x2</code><br>
      <sub>Temperature and humidity side by side (HTS221)</sub><br>
      <sub>SSIM&nbsp;0.8706&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/04_circular_gauge/main.py'>Circular Gauge</a></strong><br><br>
      <img src='04_circular_gauge.svg' width='180' title='SVG reference'>&nbsp;<img src='04_circular_gauge_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.gauge(dist, min_val, max_val, unit)</code><br>
      <sub>Distance visualized as a circular arc gauge (VL53L1X ToF)</sub><br>
      <sub>SSIM&nbsp;0.8788&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/05_scrolling_graph/main.py'>Scrolling Graph</a></strong><br><br>
      <img src='05_scrolling_graph.svg' width='180' title='SVG reference'>&nbsp;<img src='05_scrolling_graph_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.graph(data, min_val, max_val)</code><br>
      <sub>Light level history as a scrolling line graph (APDS9960)</sub><br>
      <sub>SSIM&nbsp;0.8859&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/06_dpad_menu/main.py'>D-pad Menu</a></strong><br><br>
      <img src='06_dpad_menu.svg' width='180' title='SVG reference'>&nbsp;<img src='06_dpad_menu_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.menu(items, selected)</code><br>
      <sub>Scrollable menu navigated with D-pad buttons (MCP23009E)</sub><br>
      <sub>SSIM&nbsp;0.8671&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/07_compass/main.py'>Compass</a></strong><br><br>
      <img src='07_compass.svg' width='180' title='SVG reference'>&nbsp;<img src='07_compass_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.compass(heading)</code><br>
      <sub>Compass rose with heading needle and cardinal labels</sub><br>
      <sub>SSIM&nbsp;0.8585&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/09_watch/main.py'>Analog Watch</a></strong><br><br>
      <img src='09_watch.svg' width='180' title='SVG reference'>&nbsp;<img src='09_watch_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.watch(hours, minutes, seconds)</code><br>
      <sub>Classical analog watch face with hour, minute and second hands</sub><br>
      <sub>SSIM&nbsp;0.8929&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_happy/main.py'>Smiley — Happy</a></strong><br><br>
      <img src='08_smiley_happy.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_happy_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face('happy')</code><br>
      <sub>Full-screen happy face expression</sub><br>
      <sub>SSIM&nbsp;0.9879&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_sad/main.py'>Smiley — Sad</a></strong><br><br>
      <img src='08_smiley_sad.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_sad_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face('sad')</code><br>
      <sub>Full-screen sad face expression</sub><br>
      <sub>SSIM&nbsp;0.9879&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_surprised/main.py'>Smiley — Surprised</a></strong><br><br>
      <img src='08_smiley_surprised.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_surprised_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face('surprised')</code><br>
      <sub>Full-screen surprised face expression</sub><br>
      <sub>SSIM&nbsp;0.9879&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_angry/main.py'>Smiley — Angry</a></strong><br><br>
      <img src='08_smiley_angry.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_angry_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face('angry')</code><br>
      <sub>Full-screen angry face expression</sub><br>
      <sub>SSIM&nbsp;0.9879&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_sleeping/main.py'>Smiley — Sleeping</a></strong><br><br>
      <img src='08_smiley_sleeping.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_sleeping_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face('sleeping')</code><br>
      <sub>Full-screen sleeping face expression</sub><br>
      <sub>SSIM&nbsp;0.9879&nbsp;✅</sub>
    </td>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_love/main.py'>Smiley — Love</a></strong><br><br>
      <img src='08_smiley_love.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_love_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face('love')</code><br>
      <sub>Full-screen love face expression</sub><br>
      <sub>SSIM&nbsp;0.9879&nbsp;✅</sub>
    </td>
  </tr>
  <tr>
    <td align='center' valign='top' width='50%'>
      <strong><a href='../../tutorials/08_smiley_reactive/main.py'>Smiley — Reactive</a></strong><br><br>
      <img src='08_smiley_reactive.svg' width='180' title='SVG reference'>&nbsp;<img src='08_smiley_reactive_sim.png' width='180' title='Simulation'><br>
      <sub>SVG&nbsp;reference&nbsp;&nbsp;·&nbsp;&nbsp;Simulation</sub><br>
      <br><code>screen.face(mood, compact=True)</code><br>
      <sub>Compact face with title and mood label, reactive to sensor input</sub><br>
      <sub>SSIM&nbsp;0.9732&nbsp;✅</sub>
    </td>
    <td></td>
  </tr>
</table>

---
*Generated by [`generate_report.py`](../../generate_report.py)*
