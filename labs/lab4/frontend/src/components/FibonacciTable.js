import React from "react";

import { Table } from "antd";

class FibonacciTable extends React.Component {
    constructor(props) {
        super(props);

        this.columns = [{
            title: 'Index',
            dataIndex: 'key',
            key: 'key',
        }, {
            title: 'Value',
            dataIndex: 'value',
            key: 'value',
        }];
    }

    render() {
        const data = Object.entries(this.props.data).map(entry => {
            return { key: entry[0], value: entry[1] }
        });

        return (
            <Table dataSource={data} columns={this.columns} />
        );
    }
}

export default FibonacciTable;
