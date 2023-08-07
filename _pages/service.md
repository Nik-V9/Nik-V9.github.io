---
layout: page
permalink: /service/
title: Service & Outreach
description: 
nav: true
nav_order: 3
horizontal: false
---

<!-- pages/service.md -->
<div class="projects">
<h2 class="category">Co-organized Events</h2>
<!-- Display service -->
  {%- assign sorted_service = site.service | sort: "importance" -%}
  <!-- Generate cards for each service -->
  {% if page.horizontal -%}
  <div class="container">
    <div class="row row-cols-2">
    {%- for service in sorted_service -%}
      {% include service_horizontal.html %}
    {%- endfor %}
    </div>
  </div>
  {%- else -%}
  <div class="grid">
    {%- for service in sorted_service -%}
      {% include service.html %}
    {%- endfor %}
  </div>
  {%- endif -%}
</div>

<div class="projects">
<h2 class="category">Reviewer</h2>
</div>

**Journal:** IEEE Robotics and Automation Letters (RA-L)

**Conference:** CVPR 2023, ICRA 2023, ECCV 2022, IROS 2022, ICRA 2022, IROS 2021