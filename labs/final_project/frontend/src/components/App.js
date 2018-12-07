import axios from "axios";

import React from "react";

import autoBind from "react-autobind";
import Websocket from 'react-websocket';

import "./App.css";

import { Card } from 'antd';

import CalcForm from "./CalcForm";
import { Calc_success, Calc_triggered } from "./Notification";
import FibonacciTable from "./FibonacciTable";


class App extends React.PureComponent {
    constructor(props) {
        super(props);
        autoBind(this);
        this.state = {
            session_id: null,
            data: {}
        };
        this.host = window.location.host;
    }

    render() {
        return (
            <div className="App">
                <Websocket url={`wss://${this.host}/api/notification/notification`} onMessage={this.handleData} />
                <Card title="Fibonacci Caculator">
                    <CalcForm onSubmitCalc={this.onSubmitCalc} />
                </Card>
                <FibonacciTable data={this.state.data } />
            </div>
        );
    }

    async onSubmitCalc(index) {
        var params = new URLSearchParams();
        params.append('session_uuid', this.state.session_id);
        const response = await axios.post(`https://${this.host}/api/backend/fibonacci/${index}`, params);
        const result = response.data;
        switch(result.type) {
            case "MISS": {
                Calc_triggered(index);
                break;
            }
            case "CACHED": {
                this.updateFibonacciTable(index, result.value);
                break;
            }
            default: {
                break;
            }
        }
    }

    updateFibonacciTable(index, value) {
        if (!(index in this.state)) {
            const newData = { ...this.state.data };
            newData[index] = value;
            this.setState({
                data: newData
            });
        }
    }

    handleData(data) {
        var message = JSON.parse(data);
        switch(message.type) {
            case "CONNECT": {
                console.log({ session_id: message.id });
                this.setState({ session_id: message.id });
                break;
            }
            case "NOTIFICATION_CACULATION_SUCCESS": {
                const index = message.index;
                Calc_success(index);
                this.onSubmitCalc(index);
                break;
            }
            default: {
                break;
            }
        }
    }
}

export default App;
