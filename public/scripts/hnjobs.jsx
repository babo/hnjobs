var

DislikeButton = React.createClass({
    getInitialState: function () {
        return {liked: true};
    },
    handleClick: function () {
        console.dir(this.props);
        this.setState({liked: !this.state.liked});
    },
    render: function () {
        var text = this.state.liked ? 'No way' : 'Like';
        return (
            <p>
                <button onClick={this.handleClick} type="button" className="btn btn-sn btn-success">{text}</button>
            </p>
        );
    }
}),

Comment = React.createClass({
    render: function () {
        var rawMarkup = this.props.children.toString(),
            p = rawMarkup.indexOf('<p>'),
            title = p === -1 ? rawMarkup : rawMarkup.substring(0, p),
            body = p === -1 ? '' : rawMarkup.substring(p);
        return (
            <div className='comment list-group-item'>
                <h4 className="list-group-item-heading" dangerouslySetInnerHTML={{__html: title}}></h4>
                <div className='list-group-item-text'>
                    <span dangerouslySetInnerHTML={{__html: body}} />
                    <h5>
                        <span className='commentAuthor label label-info' >
                            <a target="_blank" href={"https://news.ycombinator.com/user?id=" + this.props.author}>{this.props.author}</a>
                        </span>
                    </h5>
                    <DislikeButton postid={this.props}/>
                </div>
            </div>
        );
    }
}),

CommentList = React.createClass({
    render: function () {
        var commentNodes = this.props.data.map(function (comment) {
            return (
                <Comment author={comment.by}  key={comment.id}>
                    {comment.text}
                </Comment>
            );
        });
        return (
            <div className='commentList list-group'>
                {commentNodes}
            </div>
        );
    }
}),

CommentBox = React.createClass({
    loadCommentsFromServer: function () {
        $.ajax({
            url: this.props.url,
            dataType: 'json',
            success: function (data) {
                this.setState({data: data});
            }.bind(this),
            error: function (xhr, status, err) {
                console.error(this.props.url, status, err.toString());
            }.bind(this)
        });
    },
    getInitialState: function () {
        return {data: []};
    },
    componentDidMount: function () {
        this.loadCommentsFromServer();
        if (this.props.pollInterval !== undefined) {
            setInterval(this.loadCommentsFromServer, this.props.pollInterval);
        }
    },
    render: function () {
        return (
            <div className='commentBox'>
                <h1>Jobs</h1>
                <CommentList data={this.state.data} />
            </div>
        );
    }
});

React.render(
    <CommentBox url='/hnjobs' pollInterval2={2000}/>,
    document.getElementById('content')
);
