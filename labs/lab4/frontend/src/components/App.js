import axios from "axios";

import React from "react";

import autoBind from "react-autobind";
import Websocket from 'react-websocket';

import "./App.css";

import { Card, Button } from 'antd';

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
    }

    render() {
        console.log(this.state);
        return (
            <div className="App">
                <Websocket url='ws://localhost:8888/notification' onMessage={this.handleData} />
                <Card title="Fibonacci Caculator">
                    <CalcForm onSubmitCalc={this.onSubmitCalc} />
                </Card>
                <FibonacciTable data={this.state.data } />
            </div>
        );
    }

    async onSubmitCalc(index) {
        const response = await axios.post(`http://localhost:5000/fibonacci/${index}`, null, { headers: { session_uuid: this.state.session_id }});
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

    onCalcCompelete = () => {
        Calc_success(1);
        //Calc_success(index);
        this.setState({
            data: {
                0 : 1,
                1 : 1,
                2 : 2,
                3 : 3,
                4 : 5,
                5 : 8,
                6 : 13,
                7 : 21
            }
        })
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
        console.log(data);
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
