{
  "title": "Rust Power Manager: Battery Notifications on i3wm",
  "publishDate": "2024-10-02T09:00:00+09:00",
  "draft": false,
  "url": "/20241002/Rust20241002.html",
  "params": {
    "legacy": true
  },
  "description": "For context I'm running my laptop on PopOS with i3wm. My laptop getting a bit old now the battery is a bit tired :D."
}

## Rust take the bus

Hi there,

This time I have been working on a project which was use-full to me.

For context I'm running my laptop on PopOS with i3wm. My laptop getting a bit old now the battery is a bit tired :D.

i3wm being a you configure it all manual Window Manager, and by default I don't have or I'm not aware out-of-the-box to get a notification when my battery is getting low. I decide to use the opportunity to develop the tool myself.

### This was a very good learning experience.

- To learn about the basics of the notification bus of X11 ( yeah I know should learn about Wayland but i feel it not ready yet )
- To learn about Systemd services deployments. ( Spoiler: I really don't like Systemd, I find it messy )
- To continue learning about Rust ( I still like it even if the hype went down :D )

#### First step talk to dbus

*use dbus::blocking::Connection;*

*use dbus::{Message, arg::messageitem::MessageItemArray};*

*use std::{time::Duration, vec};*

*pub fn prendlebus() -\> Result\<(), Box\<dyn std::error::Error\>\> {*

* let timeout = Duration::new(2000,0);*

* // First open up a connection to the session bus.*

* let conn = Connection::new_session()?;*

* *

* // Create a message that calls the Notify method of the Notifications interface*

* let mut m = Message::new_method_call(*

* "org.freedesktop.Notifications", // destination*

* "/org/freedesktop/Notifications", // path*

* "org.freedesktop.Notifications", // interface*

* "Notify" // method*

* ).unwrap();*

* *

* // Append the required arguments to the message*

* let notificationlevel: u32 = 0;*

* let actions = MessageItemArray::new(vec\![\],"as".into()).unwrap();*

* let hints = MessageItemArray::new(vec\![\],"a{sv}".into()).unwrap();*

* let timingout = 5000;*

* m = Message::append3(m,"bll",notificationlevel,"/usr/share/icons/ubuntu-mono-dark/status/24/unity-battery-020.svg")*

* .append3("BATTERY", "Your Battery is running low !!", actions)*

* .append2(hints, timingout);*

* // Send the message to the bus and handle the possible errors*

* match conn.channel().send_with_reply_and_block(m, timeout){*

* //match conn.send_with_reply_and_block(m, 2000) {*

* Ok(\_) =\> println!("Notification sent successfully"),*

* Err(e) =\> println!("Error: {}", e),*

* }*

* Ok(())*

*} *

#### Then Get the battery level and status

*use std::fs;*

*use bll::prendlebus;*

*fn main() {*

* *

* let warning_value = 600000;*

* let battery_level = "/sys/class/power_supply/BAT1/charge_now";*

* let battery_status = "/sys/class/power_supply/BAT1/status";*

* println!("Check from {}", battery_level);*

* let current_battery_level = fs::read_to_string(battery_level)*

* .expect("Should have been able to read the file")*

* .as_str()*

* .trim()*

* .parse::\<u32\>()*

* .unwrap();*

* let current_battery_status: String = fs::read_to_string(battery_status).expect("should be ok").trim().parse().unwrap();*

* //println!("{:#?}",&current_battery_status);*

* //println!("This is the content: {}",current_battery_level);*

* *

* // if current now is lower than warning_value*

* // trigger dbus nofitication*

* *

* *

* if current_battery_level \<= warning_value {*

* if current_battery_status == "Discharging" {*

* println!("Battery is going to ie !! See {warning_value} \> {current_battery_level}");*

* let \_ = prendlebus();*

* } else {*

* print!("We are charging all good!\n")*

* }*

* }*

*}*

#### Finally run the binary through Systemd service.

This is the configuration file to create the service

*\[Unit\]*

*Description=Battery Low Level*

*\[Service\]*

*Type=oneshot*

*ExecStart=/devouille/bll/target/release/bll*

*User=mducorps*

This is the timer to run it every 30sec

*\[Unit\]*

*Description=Bll timer*

*\[Timer\]*

*OnUnitActiveSec=30s*

*OnBootSec=30s*

*\[Install\]*

*WantedBy=timers.target*

With this I have now a desktop notification when my laptop is running low on Battery. working flawlessly so far.

You can find the source code here.

<https://github.com/Vagrantin/bll>

With kind regards

Matthieu.
