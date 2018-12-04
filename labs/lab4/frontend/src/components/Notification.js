import { notification } from 'antd';

export const Calc_success = (index) => {
    notification["success"]({
      message: 'Calculation complete',
      description: `${index}th of fibonacci calculation completed.`,
    });
};

export const Calc_triggered = (index) => {
    notification["info"]({
        message: 'Calulation is triggered',
        description: `${index}th of fibonacci calculation is triggered.`
    })
}
