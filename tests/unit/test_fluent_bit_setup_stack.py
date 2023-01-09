import aws_cdk as core
import aws_cdk.assertions as assertions

from fluent_bit_setup.fluent_bit_setup_stack import FluentBitSetupStack

# example tests. To run these tests, uncomment this file along with the example
# resource in fluent_bit_setup/fluent_bit_setup_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = FluentBitSetupStack(app, "fluent-bit-setup")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
