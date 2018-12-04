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
var Button = function Button(_ref) {
    var _ref$variant = _ref.variant,
        variant = _ref$variant === undefined ? "primary" : _ref$variant,
        text = _ref.text,
        size = _ref.size,
        className = _ref.className,
        onClick = _ref.onClick,
        _ref$type = _ref.type,
        type = _ref$type === undefined ? "button" : _ref$type;

    var classPrefix = "btn";
    var classes = classNames(className, classPrefix, classPrefix + "-" + variant, size && classPrefix + "-" + size);
    return React.createElement(
        "button",
        { className: classes, onClick: onClick, type: type },
        text
    );
};

var Icon = function Icon(_ref2) {
    var _ref2$variant = _ref2.variant,
        variant = _ref2$variant === undefined ? "alert" : _ref2$variant,
        _ref2$className = _ref2.className,
        className = _ref2$className === undefined ? "mx-1" : _ref2$className;

    return React.createElement("img", { className: className, style: { width: "20px", height: "20px" }, src: "/static/octicons/" + variant + ".svg" });
};