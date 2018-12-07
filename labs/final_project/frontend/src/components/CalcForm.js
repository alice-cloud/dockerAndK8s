import React from "react";

import {
    Form, InputNumber, Button, Icon
  } from 'antd';
  
const FormItem = Form.Item;

class CalcForm extends React.Component {
    handleSubmit = (e) => {
      e.preventDefault();
      this.props.form.validateFields((err, values) => {
        if (!err) {
          this.props.onSubmitCalc(values.Index);
        }
      });
    }

    render() {
        const { getFieldDecorator } = this.props.form;

        return (
            <Form onSubmit={this.handleSubmit} layout="inline">
                <FormItem>
                {getFieldDecorator('Index', {
                    rules: [

                        { required: true, message: 'Please input your fibonacci index!' },
                        { type: 'integer', min: 0, message: '>=0' },
                        { type: 'integer', max: 50, message: '<=50' }
                    ],
                })(
                    <InputNumber prefix={<Icon type="number" style={{ color: 'rgba(0,0,0,.25)' }} />} placeholder="Index" />
                )}
                </FormItem>
                <FormItem>
                    <Button type="primary" htmlType="submit">
                        Caculate
                    </Button>
                </FormItem>
            </Form>
        );
    }
}

export default Form.create()(CalcForm);
