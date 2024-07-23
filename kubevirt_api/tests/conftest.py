# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)
import os
import time
from contextlib import ExitStack

import pytest

from datadog_checks.dev import get_here, run_command
from datadog_checks.dev.http import MockResponse
from datadog_checks.dev.kind import kind_run
from datadog_checks.dev.kube_port_forward import port_forward

HERE = get_here()


KUBEVIRT_VERSION = "v1.2.2"


def setup_kubevirt():
    # deploy the KubeVirt operator
    run_command(["kubectl", "create", "-f", os.path.join(HERE, "kind", "kubevirt-operator.yaml")])

    # deploy the KubeVirt Custom Resource Definitions
    run_command(["kubectl", "create", "-f", os.path.join(HERE, "kind", "kubevirt-cr.yaml")])

    # enable nested virtualization
    run_command(
        [
            "kubectl",
            "-n",
            "kubevirt",
            "patch",
            "kubevirt",
            "kubevirt",
            "--type=merge",
            "--patch",
            '{"spec":{"configuration":{"developerConfiguration":{"useEmulation":true}}}}',
        ]
    )
    time.sleep(30)

    # wait for kubevirt deployment
    run_command(
        [
            "kubectl",
            "wait",
            "kubevirt.kubevirt.io/kubevirt",
            "-n",
            "kubevirt",
            "--for=jsonpath={.status.phase}=Deployed",
            "--timeout=2m",
        ]
    )

    time.sleep(10)

    # deploy a VirtualMachine instance
    run_command(["kubectl", "apply", "-f", os.path.join(HERE, "kind", "vm.yaml")])
    run_command(["kubectl", "patch", "virtualmachine", "testvm", "--type", "merge", "-p", '{"spec":{"running":true}}'])


@pytest.fixture(scope="session")
def dd_environment():
    with kind_run(conditions=[setup_kubevirt], sleep=60) as kubeconfig, ExitStack() as stack:
        instance = {}

        host, port = stack.enter_context(port_forward(kubeconfig, "kubevirt", 443, "service", "virt-api"))
        instance["kubevirt_api_url"] = f"https://{host}:{port}/metrics"
        instance["health_url"] = f"https://{host}:{port}/healthz"

        yield {"instances": [instance]}


@pytest.fixture
def instance():
    return {
        "kubevirt_api_url": "https://virt-api.kubevirt.svc/metrics",
        "health_url": "https://virt-api.kubevirt.svc/healthz",
    }


@pytest.fixture
def healthz_path():
    return os.path.join(get_here(), "fixtures", "healthz.txt")


def mock_http_responses(url, **_params):
    mapping = {
        "https://virt-api.kubevirt.svc/healthz": "healthz.txt",
        "https://virt-api.kubevirt.svc/metrics": "metrics.txt",
    }

    fixtures_file = mapping.get(url)

    if not fixtures_file:
        raise Exception(f"url `{url}` not registered")

    with open(os.path.join(HERE, "fixtures", fixtures_file)) as f:
        return MockResponse(content=f.read())
