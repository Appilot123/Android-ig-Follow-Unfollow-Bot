# Instagram Follow Unfollow Bot (Android) — Real-Device Automation

> Free, self-hosted **Android** automation for Instagram: **follow & unfollow** (plus share reels/posts).  
> A production-ready **instagram follow unfollow bot** with human-like pacing, retries, logs, and safe daily caps.

## Contact us
<p align="center">
  <a href="https://discord.gg/zX7frTbx">
    <img alt="Discord contact for instagram follow unfollow bot support" src="https://img.shields.io/badge/Discord-Appilot-5865F2?logo=discord&logoColor=white&style=for-the-badge">
  </a>
  <a href="https://t.me/devpilot1">
    <img alt="Telegram contact for android instagram automation bot" src="https://img.shields.io/badge/Telegram-@devpilot1-2CA5E0?logo=telegram&logoColor=white&style=for-the-badge">
  </a>
</p>

> instagram follow unfollow bot · follow unfollow bot · instagram follow and unfollow bot · unfollow bot instagram · automatic follow unfollow instagram

---

## Introduction
This project is a **real-device Instagram follow/unfollow bot** for Android phones and emulators. It queues tasks, paces actions like a human (random delays, jitter, cooldowns), and logs every step for safe re-runs. Start with **follow/unfollow** plus share features; scale from one phone to a 50+ device farm.

**Field usage:** used to manage **2,000+ accounts** with **<1% block rate** when following conservative schedules, cooldowns, and quality proxies. *(Results vary by account age, content, and network.)*

---

<img width="1536" height="500" alt="instagram follow unfollow bot android real-device automation dashboard" src="https://github.com/user-attachments/assets/1fe0bce2-03af-46f4-9063-0d8160cbb419" />

---

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Try it for free](#try-it-for-free)
- [Video Demo](#video-demo)
- [Workflow](#workflow)
- [Workflow image](#workflow-image)
- [Key Stats](#key-stats)
- [FAQ](#faq)
- [Contact us](#contact-us)

---

## Overview
The bot drives **real Android devices** (ADB/Appium/Accessibility) to perform Instagram actions with **rate-limit-safe** rules: randomized delays, session caps, cooldowns, night mode windows, and error-aware retries. It supports **campaign queues**, **structured JSON logs**, and **idempotent replays**.  
This repository focuses on the free actions below; the Pro suite (Likes, Comments, Stories, Posting, DMs, advanced scheduler, farm manager, etc.) lives in the Pro repo.

---

## Features

| # | Feature | Description |
|---|---|---|
| 1 | **Follow** | Follow targets from hashtags, Explore, suggested users, mutuals, or profile followers, with **human-like delays**, per-action caps, and jitter. |
| 2 | **Unfollow** | Smart **unfollow bot instagram** modes: unfollow-all, **whitelist-except**, and **last-followed-only**, with safe **daily limits**. |
| 3 | **Share reels** | Share any reel to DMs or a story share queue (share action). |
| 4 | **Share posts** | Share feed posts to DMs or a story share queue (share action). |
| 5 | **Scheduling** | **Automatic follow unfollow instagram** via one-time or daily recurring jobs per device. |
| 6 | **Anti-block controls** | Randomized pacing, cooldowns, session caps, and built-in retries with backoff. |
| 7 | **Accessibility auto-fix** | Automatically re-enables Accessibility Service if Android resets it. |
| 8 | **Scroll recovery** | Handles empty lists, UI changes, and infinite scroll safely. |
| 9 | **Task replacement** | Prevents duplicate work by overwriting older schedules for a device. |
| 10 | **In-app logs & status** | Track success/failure and device connection health from the home screen. |
| 11 | **Multi-device scaling** | Orchestrate **10/20/50+** devices via a cloud/web dashboard. |
| 12 | **Roadmap** | AI filter to skip brand/business accounts; **offline task queuing** when a device is briefly offline. |

> Secondary keywords used naturally: *instagram follow and unfollow bot*, *automate instagram follow unfollow*, *follow and unfollow bot*, *auto unfollow bot instagram*.

---

## Try it for free

<img width="1536" height="500" alt="try instagram follow unfollow bot free real device automation" src="https://github.com/user-attachments/assets/199762ad-d32e-4690-8b26-3fc5e214db40" />

---

## Video Demo

<p align="center">
  <img src="https://github.com/user-attachments/assets/480b9ec7-05ac-4ea8-b3f7-6005335fbc36"
       alt="instagram follow unfollow bot demo on android device"
       width="250px" />
</p>

<div align="center">
  <a href="https://youtu.be/csCvtgMORN8?si=_bu5rPxWCobUaCmH">
    <img
      alt="Watch full demo of instagram follow unfollow bot on YouTube"
      width="25px"
      src="https://github.com/user-attachments/assets/c685ef52-2bdd-464c-bd60-cc6e34e8e867"
    />
    <code>Full Video Demo on YouTube</code>
  </a>
</div>

---

## Workflow

1) **Connect devices** (ADB/Appium/Accessibility) → verify health, SIM/proxy, storage.  
2) **Load campaign** (targets, limits, schedules).  
3) **Humanizer** applies dwell/scroll/jitter and safe pacing.  
4) **Executor** runs actions with retries + backoff; screenshots on error.  
5) **Logger** writes per-step JSON; aggregates a run report.  
6) **Review** results; resume failed steps idempotently.

---

## Workflow image

<img width="1536" height="500" alt="instagram follow and unfollow bot workflow architecture android appium accessibility" src="https://github.com/user-attachments/assets/d63c2611-11bf-48ce-8f62-d7a9aeb44bde" />

---

## Key Stats
- **Success rate:** 95%  
- **Latency (per action):** ~3s  
- **Throughput (per device):** ~**140** follows/day · **55–70** shares/day  
- **Reliability:** retry **3–5%** · final fail **≤0.6%** · MTTR **~45–75s**  
- **Scale/Uptime:** **~12** devices/controller comfortably · **99.6%** 30-day uptime  
- **Field usage:** managed **2,000+ accounts** with **<1% block rate** using conservative schedules & cooldowns

---

## FAQ

**Do bots follow and unfollow on Instagram?**  
Yes. This **instagram follow unfollow bot** performs follow/unfollow with **safe pacing**, randomized delays, and session caps to reduce flags.

**How does follow unfollow work on Instagram?**  
You follow a targeted audience (hashtags, Explore, mutuals, profile followers), then **unfollow** later using modes like **whitelist-except** or **last-followed-only** to keep your graph clean.

**Are there risks in using bot followers?**  
Any automation can be detected. Mitigate with **aged accounts**, **quality mobile/residential proxies**, **cooldowns**, night windows, and **conservative daily limits**.

**How do Instagram follow bots work?**  
On Android, the bot uses **Accessibility** to tap, type, and scroll with jitter; adds retries and recovery logic for UI changes or empty lists.

**What is the fastest way to remove followers on Instagram?**  
Use **smart unfollow-all** or **last-followed-only** with **safe pacing**—avoid burst removal; keep to daily caps to prevent rate-limit spikes.

---

## Contact us
<p align="center">
  <a href="https://discord.gg/zX7frTbx">
    <img alt="Discord contact for instagram follow unfollow bot support" src="https://img.shields.io/badge/Discord-Appilot-5865F2?logo=discord&logoColor=white&style=for-the-badge">
  </a>
  <a href="https://t.me/devpilot1">
    <img alt="Telegram contact for android instagram automation bot" src="https://img.shields.io/badge/Telegram-@devpilot1-2CA5E0?logo=telegram&logoColor=white&style=for-the-badge">
  </a>
</p>

---
