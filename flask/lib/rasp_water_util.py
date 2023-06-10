#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import (
    jsonify,
    Blueprint,
)
import os
import subprocess
import re
import psutil
import tracemalloc

from rasp_water_config import APP_PATH
from flask_util import support_jsonp

blueprint = Blueprint("rasp-water-util", __name__, url_prefix=APP_PATH)

snapshot_prev = None


@blueprint.route("/api/memory", methods=["GET"])
@support_jsonp
def print_memory():
    return {"memory": psutil.Process(os.getpid()).memory_info().rss}


# NOTE: メモリリーク調査用
@blueprint.route("/api/snapshot", methods=["GET"])
@support_jsonp
def snap():
    global snapshot_prev

    if not snapshot_prev:
        tracemalloc.start()
        snapshot_prev = tracemalloc.take_snapshot()

        return {"msg": "taken snapshot"}
    else:
        lines = []
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.compare_to(snapshot_prev, "lineno")
        snapshot_prev = snapshot

        for stat in top_stats[:10]:
            lines.append(str(stat))

        return jsonify(lines)


@blueprint.route("/api/sysinfo", methods=["GET"])
@support_jsonp
def api_sysinfo():
    date = (
        subprocess.Popen(["date", "-R"], stdout=subprocess.PIPE)
        .communicate()[0]
        .decode()
        .strip()
    )

    uptime = (
        subprocess.Popen(["uptime", "-s"], stdout=subprocess.PIPE)
        .communicate()[0]
        .decode()
        .strip()
    )

    loadAverage = re.search(
        r"load average: (.+)",
        subprocess.Popen(["uptime"], stdout=subprocess.PIPE).communicate()[0].decode(),
    ).group(1)

    return jsonify({"date": date, "uptime": uptime, "loadAverage": loadAverage})
