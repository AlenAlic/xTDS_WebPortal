//class Button extends React.Component {
//    constructor(props) {
//        super(props);
//    }
//    static defaultProps = {classPrefix: 'btn', variant: 'primary', active: false, disabled: false, type: 'button'};
//    render() {
//        const {classPrefix, variant, active, disabled, type, className, size, onClick, label, ...props} = this.props;
//        const classes = classNames(className, classPrefix, `${classPrefix}-${variant}`, size && `${classPrefix}-${size}`);
//        return <div><button {...props} className={classes} onClick={this.props.onClick}>{label}</button></div>
//    }
//}
const Button = ({variant="primary", text, size, className, onClick, type="button"}) => {
    const classPrefix = "btn"
    const classes = classNames(className, classPrefix, `${classPrefix}-${variant}`, size && `${classPrefix}-${size}`);
    return (
        <button className={classes} onClick={onClick} type={type}>{text}</button>
    )
}

const Icon = ({variant="alert", className="mx-1"}) => {
    return (
        <img className={className} style={{width:"20px", height:"20px"}} src={`/static/octicons/${variant}.svg`}/>
    )
}
